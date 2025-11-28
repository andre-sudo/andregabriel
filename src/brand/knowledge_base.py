"""
Brand Knowledge Base - Storage and retrieval of brand profiles

This is the "memory" system of the Brand World Model,
persisting learned brand patterns for future use.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .schemas import BrandSchema, TemplateSchema, SlideSchema


class BrandKnowledgeBase:
    """
    Manages storage and retrieval of brand profiles.

    The knowledge base acts as the persistent memory of the world model,
    storing learned patterns and enabling retrieval for template generation.
    """

    def __init__(self, storage_path: str = "./data/brands"):
        """
        Initialize the knowledge base.

        Args:
            storage_path: Directory to store brand profiles
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, BrandSchema] = {}

    def save_brand(self, brand: BrandSchema) -> str:
        """
        Save a brand profile to the knowledge base.

        Args:
            brand: BrandSchema to save

        Returns:
            Brand ID
        """
        # Update timestamp
        brand_dict = brand.model_dump()
        brand_dict['updated_at'] = datetime.now().isoformat()
        if not brand_dict.get('created_at'):
            brand_dict['created_at'] = brand_dict['updated_at']

        # Save to file
        file_path = self.storage_path / f"{brand.id}.json"
        with open(file_path, 'w') as f:
            json.dump(brand_dict, f, indent=2)

        # Update cache
        self._cache[brand.id] = BrandSchema(**brand_dict)

        return brand.id

    def get_brand(self, brand_id: str) -> Optional[BrandSchema]:
        """
        Retrieve a brand profile by ID.

        Args:
            brand_id: The brand identifier

        Returns:
            BrandSchema or None if not found
        """
        # Check cache first
        if brand_id in self._cache:
            return self._cache[brand_id]

        # Load from file
        file_path = self.storage_path / f"{brand_id}.json"
        if not file_path.exists():
            return None

        with open(file_path, 'r') as f:
            data = json.load(f)

        brand = BrandSchema(**data)
        self._cache[brand_id] = brand
        return brand

    def list_brands(self) -> List[Dict[str, str]]:
        """
        List all stored brand profiles.

        Returns:
            List of brand summaries (id, name, updated_at)
        """
        brands = []
        for file_path in self.storage_path.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                brands.append({
                    "id": data.get("id", file_path.stem),
                    "name": data.get("name", "Unknown"),
                    "updated_at": data.get("updated_at", ""),
                    "confidence": data.get("confidence_score", 0)
                })
            except (json.JSONDecodeError, KeyError):
                continue

        return sorted(brands, key=lambda x: x.get("updated_at", ""), reverse=True)

    def delete_brand(self, brand_id: str) -> bool:
        """
        Delete a brand profile.

        Args:
            brand_id: The brand identifier

        Returns:
            True if deleted, False if not found
        """
        file_path = self.storage_path / f"{brand_id}.json"
        if not file_path.exists():
            return False

        file_path.unlink()
        if brand_id in self._cache:
            del self._cache[brand_id]

        return True

    def update_brand(self, brand_id: str, updates: Dict[str, Any]) -> Optional[BrandSchema]:
        """
        Update specific fields of a brand profile.

        Args:
            brand_id: The brand identifier
            updates: Dictionary of fields to update

        Returns:
            Updated BrandSchema or None if not found
        """
        brand = self.get_brand(brand_id)
        if not brand:
            return None

        # Merge updates
        brand_dict = brand.model_dump()
        brand_dict.update(updates)
        brand_dict['updated_at'] = datetime.now().isoformat()

        # Validate and save
        updated_brand = BrandSchema(**brand_dict)
        self.save_brand(updated_brand)

        return updated_brand

    def add_layout_pattern(
        self,
        brand_id: str,
        layout: SlideSchema
    ) -> Optional[BrandSchema]:
        """
        Add a new layout pattern to a brand.

        Args:
            brand_id: The brand identifier
            layout: SlideSchema to add

        Returns:
            Updated BrandSchema or None if brand not found
        """
        brand = self.get_brand(brand_id)
        if not brand:
            return None

        brand_dict = brand.model_dump()
        brand_dict['layout_patterns'].append(layout.model_dump())

        return self.update_brand(brand_id, {'layout_patterns': brand_dict['layout_patterns']})

    def get_layout_for_type(
        self,
        brand_id: str,
        layout_type: str
    ) -> Optional[SlideSchema]:
        """
        Get a specific layout type from a brand.

        Args:
            brand_id: The brand identifier
            layout_type: Type of layout to retrieve

        Returns:
            SlideSchema or None if not found
        """
        brand = self.get_brand(brand_id)
        if not brand:
            return None

        for layout in brand.layout_patterns:
            if layout.layout_type.value == layout_type:
                return layout

        return None

    def search_brands(self, query: str) -> List[Dict[str, str]]:
        """
        Search brands by name or description.

        Args:
            query: Search query string

        Returns:
            List of matching brand summaries
        """
        query_lower = query.lower()
        results = []

        for file_path in self.storage_path.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)

                name = data.get("name", "").lower()
                description = data.get("description", "").lower()

                if query_lower in name or query_lower in description:
                    results.append({
                        "id": data.get("id", file_path.stem),
                        "name": data.get("name", "Unknown"),
                        "description": data.get("description", ""),
                        "confidence": data.get("confidence_score", 0)
                    })
            except (json.JSONDecodeError, KeyError):
                continue

        return results

    def export_brand(self, brand_id: str, format: str = "json") -> Optional[str]:
        """
        Export a brand profile in various formats.

        Args:
            brand_id: The brand identifier
            format: Export format (json, yaml, css)

        Returns:
            Exported content as string
        """
        brand = self.get_brand(brand_id)
        if not brand:
            return None

        if format == "json":
            return json.dumps(brand.model_dump(), indent=2)

        elif format == "yaml":
            import yaml
            return yaml.dump(brand.model_dump(), default_flow_style=False)

        elif format == "css":
            return self._export_as_css(brand)

        return None

    def _export_as_css(self, brand: BrandSchema) -> str:
        """Export brand colors and typography as CSS variables"""
        css_lines = [":root {"]

        # Colors
        for color in brand.colors:
            var_name = f"--color-{color.role.value}"
            css_lines.append(f"  {var_name}: {color.hex};")

        # Typography
        css_lines.append(f"  --font-heading: '{brand.typography.heading.family}', {', '.join(brand.typography.heading.fallback)};")
        css_lines.append(f"  --font-body: '{brand.typography.body.family}', {', '.join(brand.typography.body.fallback)};")
        css_lines.append(f"  --font-size-base: {brand.typography.body.size_base}px;")
        css_lines.append(f"  --line-height: {brand.typography.body.line_height};")

        # Spacing
        css_lines.append(f"  --spacing-unit: {brand.spacing.unit}px;")
        css_lines.append(f"  --margin-x: {brand.spacing.margin_x * brand.spacing.unit}px;")
        css_lines.append(f"  --margin-y: {brand.spacing.margin_y * brand.spacing.unit}px;")

        css_lines.append("}")

        return "\n".join(css_lines)

    def merge_brands(
        self,
        brand_ids: List[str],
        new_id: str,
        new_name: str
    ) -> Optional[BrandSchema]:
        """
        Merge multiple brand profiles into one.

        Useful for combining patterns from multiple sources.

        Args:
            brand_ids: List of brand IDs to merge
            new_id: ID for the merged brand
            new_name: Name for the merged brand

        Returns:
            Merged BrandSchema or None if no brands found
        """
        brands = [self.get_brand(bid) for bid in brand_ids]
        brands = [b for b in brands if b is not None]

        if not brands:
            return None

        # Use first brand as base
        merged = brands[0].model_dump()
        merged['id'] = new_id
        merged['name'] = new_name
        merged['source_files'] = []

        # Merge layout patterns from all brands
        all_layouts = []
        for brand in brands:
            for layout in brand.layout_patterns:
                all_layouts.append(layout.model_dump())
            merged['source_files'].extend(brand.source_files)

        merged['layout_patterns'] = all_layouts

        # Merge rules
        all_rules = []
        for brand in brands:
            for rule in brand.rules:
                all_rules.append(rule.model_dump())
        merged['rules'] = all_rules

        # Save merged brand
        merged_brand = BrandSchema(**merged)
        self.save_brand(merged_brand)

        return merged_brand
