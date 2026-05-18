'''
mapper.py
'''
import dataclasses
from dataclasses import fields, is_dataclass, asdict
from typing import Type, TypeVar, Optional

T = TypeVar("T")

class Mapper:
    @staticmethod
    def row_to_dict(row) -> dict:
        return dict(row._mapping)

    @staticmethod
    def to_entity(row, entity_class: Type[T]) -> T:
        data = dict(row._mapping)
        
        valid_keys = {f.name for f in dataclasses.fields(entity_class)}
        
        # 데이터 중 엔티티 필드에 존재하는 것만 매핑
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        
        return entity_class(**filtered_data)
    
    @staticmethod
    def dto_to_dict(dto, custom_map: Optional[dict[str, str]] = None) -> dict:
        """
        DTO(dataclass) → dict 변환

        e.g.
            data = Mapper.dto_to_dict(
                dto,
                custom_map={
                    "category": "category_id"
                }
            )
        """

        if not is_dataclass(dto):
            raise TypeError(f"{dto.__class__.__name__} is not a dataclass instance")

        data = asdict(dto)

        # 필드 이름 변경
        if custom_map:
            for src, target in custom_map.items():
                if src in data:
                    data[target] = data.pop(src)

        return data

    @staticmethod
    def to_dto(entity, dto_class: Type[T], custom_map: Optional[dict[str, str]] = None) -> T:
        '''
        e.g. Entity → DTO 변환 (추가 가공용)
            dtos = [
                Mapper.to_dto(
                    entity,
                    FaqDTO,
                    custom_map={
                        "category_id": "category"  # 필요 시 이름 변경
                    }
                )
                for entity in entities
            ]
        '''
        # entity가 dict인지 객체인지 처리
        if isinstance(entity, dict):
            data = entity.copy()
        else:
            data = vars(entity).copy()

        if not is_dataclass(dto_class):
            raise TypeError(f"{dto_class.__name__} is not a dataclass")
        
        # 필드 이름 매핑
        if custom_map:
            for src, target in custom_map.items():
                if src in data:
                    data[target] = data.pop(src)

        # DTO에 존재하는 필드만 남기기
        dto_fields = {f.name for f in fields(dto_class)}
        filtered_data = {k: v for k, v in data.items() if k in dto_fields}

        return dto_class(**filtered_data)
