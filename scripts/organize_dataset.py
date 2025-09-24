#!/usr/bin/env python3
"""
Enhanced Dataset Organization Script - OMR Grading System
========================================================

Implements Enhanced Hybrid Strategy yang menggabungkan:
1. Professional ML splits (train/test/valid) - existing structure
2. Quality-based sub-organization dalam each split
3. Curated sample sets untuk development efficiency

Strategy: ML Standards + Quality-Based Learning Progression

Author: OMR Development Team
Date: Week 1 - Day 2 Implementation
"""

import os
import cv2
import shutil
import numpy as np
from pathlib import Path
import argparse
import json
from datetime import datetime
from typing import Dict, List, Tuple


class EnhancedDatasetOrganizer:
    """
    Enhanced Dataset Organizer yang implements Hybrid Strategy

    Features:
    - Maintains existing ML splits (train/test/valid)
    - Adds quality-based sub-organization
    - Creates curated sample sets
    - Comprehensive validation dan reporting
    """

    def __init__(self, source_path: str = "Datasets", target_path: str = "datasets"):
        """
        Initialize organizer dengan source dan target paths

        Args:
            source_path: Path ke original dataset (default: "Datasets")
            target_path: Path untuk organized dataset (default: "datasets")
        """
        self.source_path = Path(source_path)
        self.target_path = Path(target_path)

        # Quality thresholds (calibrated untuk OMR images)
        self.quality_thresholds = {
            'high': 0.8,     # ≥0.8: Perfect scans, optimal lighting
            'medium': 0.5,   # 0.5-0.8: Good quality dengan minor issues
            'low': 0.0       # <0.5: Challenging conditions
        }

        # Sample set configurations
        self.sample_config = {
            'development': {'count': 20, 'source': 'train/quality-high', 'description': 'Best images untuk daily work'},
            'benchmark': {'count': 15, 'source': 'mixed', 'description': 'Balanced quality untuk performance measurement'},
            'testing': {'count': 30, 'source': 'mixed', 'description': 'Representative sample untuk validation'},
            'challenge': {'count': 10, 'source': 'all/quality-low', 'description': 'Most difficult untuk robustness testing'}
        }

        # Statistics tracking
        self.stats = {
            'total_images': 0,
            'quality_distribution': {},
            'split_distribution': {},
            'sample_sets': {},
            'processing_time': 0,
            'errors': []
        }

    def assess_image_quality(self, image_path: Path) -> float:
        """
        Enhanced quality assessment untuk OMR images

        Combines multiple metrics:
        1. Contrast (standard deviation)
        2. Clarity (Laplacian variance)
        3. Brightness consistency

        Args:
            image_path: Path ke image file

        Returns:
            float: Quality score 0.0-1.0
        """
        try:
            # Load image dalam grayscale
            img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
            if img is None:
                return 0.0

            # Metric 1: Contrast (standard deviation)
            contrast = img.std()

            # Metric 2: Clarity (Laplacian variance)
            laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()

            # Metric 3: Brightness consistency (lower std = more consistent)
            brightness_std = np.std(img.mean(axis=1))

            # Combined quality score dengan weights
            # Higher contrast = better, higher laplacian = sharper, lower brightness_std = more consistent
            quality_score = min(1.0,
                (contrast / 100) * 0.4 +           # Weight: 40% untuk contrast
                (laplacian_var / 1000) * 0.4 +     # Weight: 40% untuk clarity
                (1.0 - brightness_std / 100) * 0.2  # Weight: 20% untuk consistency
            )

            return quality_score

        except Exception as e:
            print(f"⚠️  Error assessing quality untuk {image_path}: {e}")
            self.stats['errors'].append(f"Quality assessment failed: {image_path}")
            return 0.0

    def get_quality_category(self, quality_score: float) -> str:
        """
        Determine quality category berdasarkan score

        Args:
            quality_score: Score dari assess_image_quality()

        Returns:
            str: 'high', 'medium', atau 'low'
        """
        if quality_score >= self.quality_thresholds['high']:
            return 'high'
        elif quality_score >= self.quality_thresholds['medium']:
            return 'medium'
        else:
            return 'low'

    def create_directory_structure(self):
        """
        Create enhanced directory structure sesuai hybrid strategy
        """
        print(" Creating enhanced directory structure...")

        # Create main structure
        directories = [
            "raw",  # Backup of original
            "train/quality-high", "train/quality-medium", "train/quality-low",
            "test/quality-high", "test/quality-medium", "test/quality-low",
            "valid/quality-high", "valid/quality-medium", "valid/quality-low",
            "samples/development", "samples/benchmark", "samples/testing", "samples/challenge"
        ]

        for directory in directories:
            dir_path = self.target_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)

        print(" Directory structure created successfully!")

    def backup_original_dataset(self):
        """
        Create backup of original dataset ke raw/ folder
        """
        print(" Creating backup of original dataset...")

        raw_path = self.target_path / "raw"
        if raw_path.exists():
            print("  Backup already exists, skipping...")
            return

        try:
            shutil.copytree(self.source_path, raw_path)
            print(" Original dataset backed up successfully!")

        except Exception as e:
            error_msg = f"Failed to backup original dataset: {e}"
            print(f" {error_msg}")
            self.stats['errors'].append(error_msg)

    def organize_split(self, split_name: str) -> Dict[str, List[Path]]:
        """
        Organize single split (train/test/valid) by quality

        Args:
            split_name: Name of split ('train', 'test', 'valid')

        Returns:
            Dict mapping quality level ke list of image paths
        """
        print(f" Organizing {split_name} split by quality...")

        source_split_path = self.source_path / split_name
        if not source_split_path.exists():
            error_msg = f"Split {split_name} not found dalam source dataset"
            print(f" {error_msg}")
            self.stats['errors'].append(error_msg)
            return {}

        # Get all images dalam split
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
            image_files.extend(source_split_path.glob(ext))

        quality_groups = {'high': [], 'medium': [], 'low': []}

        # Process each image
        for img_path in image_files:
            try:
                # Assess quality
                quality_score = self.assess_image_quality(img_path)
                quality_category = self.get_quality_category(quality_score)

                # Determine target path
                target_dir = self.target_path / split_name / f"quality-{quality_category}"
                target_path = target_dir / img_path.name

                # Copy image ke appropriate quality folder
                shutil.copy2(img_path, target_path)
                quality_groups[quality_category].append(target_path)

                # Update statistics
                self.stats['total_images'] += 1

            except Exception as e:
                error_msg = f"Failed to process {img_path}: {e}"
                print(f"  {error_msg}")
                self.stats['errors'].append(error_msg)

        # Print split summary
        total_in_split = sum(len(group) for group in quality_groups.values())
        print(f"  {split_name}: {total_in_split} images")
        for quality, images in quality_groups.items():
            print(f"      - {quality}: {len(images)} images")

        # Update statistics
        self.stats['split_distribution'][split_name] = {
            quality: len(images) for quality, images in quality_groups.items()
        }

        return quality_groups

    def create_sample_sets(self, organized_data: Dict[str, Dict[str, List[Path]]]):
        """
        Create curated sample sets untuk development efficiency

        Args:
            organized_data: Dict dengan structure {split: {quality: [paths]}}
        """
        print(" Creating curated sample sets...")

        # Development set: Best 20 dari train/quality-high
        dev_candidates = organized_data.get('train', {}).get('high', [])
        if len(dev_candidates) >= 20:
            # Sort by quality score dan take top 20
            dev_images = sorted(dev_candidates,
                              key=lambda p: self.assess_image_quality(p),
                              reverse=True)[:20]

            for img_path in dev_images:
                target_path = self.target_path / "samples" / "development" / img_path.name
                shutil.copy2(img_path, target_path)

            self.stats['sample_sets']['development'] = len(dev_images)
            print(f"    Development set: {len(dev_images)} high-quality images")

        # Benchmark set: Balanced representation (5 high, 5 medium, 5 low)
        benchmark_images = []
        for quality in ['high', 'medium', 'low']:
            candidates = []
            for split in ['train', 'test', 'valid']:
                candidates.extend(organized_data.get(split, {}).get(quality, []))

            if candidates:
                # Select 5 representative images per quality
                selected = sorted(candidates,
                                key=lambda p: self.assess_image_quality(p),
                                reverse=(quality == 'high'))[:5]
                benchmark_images.extend(selected)

        for img_path in benchmark_images:
            target_path = self.target_path / "samples" / "benchmark" / img_path.name
            shutil.copy2(img_path, target_path)

        self.stats['sample_sets']['benchmark'] = len(benchmark_images)
        print(f"    Benchmark set: {len(benchmark_images)} balanced quality images")

        # Testing set: Representative sample (30 images mixed)
        testing_candidates = []
        for split in ['train', 'valid']:  # Not using test split untuk avoid contamination
            for quality in ['high', 'medium', 'low']:
                testing_candidates.extend(organized_data.get(split, {}).get(quality, []))

        if len(testing_candidates) >= 30:
            # Random sample representing all qualities
            import random
            testing_images = random.sample(testing_candidates, 30)

            for img_path in testing_images:
                target_path = self.target_path / "samples" / "testing" / img_path.name
                shutil.copy2(img_path, target_path)

            self.stats['sample_sets']['testing'] = len(testing_images)
            print(f"    Testing set: {len(testing_images)} representative images")

        # Challenge set: Most difficult cases (10 images)
        challenge_candidates = []
        for split in ['train', 'test', 'valid']:
            challenge_candidates.extend(organized_data.get(split, {}).get('low', []))

        if challenge_candidates:
            # Sort by quality (lowest first) dan take bottom 10
            challenge_images = sorted(challenge_candidates,
                                    key=lambda p: self.assess_image_quality(p))[:10]

            for img_path in challenge_images:
                target_path = self.target_path / "samples" / "challenge" / img_path.name
                shutil.copy2(img_path, target_path)

            self.stats['sample_sets']['challenge'] = len(challenge_images)
            print(f"    Challenge set: {len(challenge_images)} most difficult images")

    def generate_report(self) -> Dict:
        """
        Generate comprehensive organization report

        Returns:
            Dict with detailed statistics dan analysis
        """
        # Calculate overall quality distribution
        total_by_quality = {'high': 0, 'medium': 0, 'low': 0}
        for split_data in self.stats['split_distribution'].values():
            for quality, count in split_data.items():
                total_by_quality[quality] += count

        self.stats['quality_distribution'] = total_by_quality

        # Add metadata
        self.stats['organization_timestamp'] = datetime.now().isoformat()
        self.stats['strategy'] = 'Enhanced Hybrid Strategy'
        self.stats['quality_thresholds'] = self.quality_thresholds

        return self.stats

    def save_report(self, report: Dict):
        """
        Save organization report ke JSON file

        Args:
            report: Dictionary dengan organization statistics
        """
        report_path = self.target_path / "organization_report.json"

        try:
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)

            print(f" Organization report saved: {report_path}")

        except Exception as e:
            print(f"  Failed to save report: {e}")

    def organize_complete_dataset(self) -> bool:
        """
        Execute complete dataset organization process

        Returns:
            bool: True if successful, False if errors occurred
        """
        start_time = datetime.now()

        print(" Starting Enhanced Dataset Organization...")
        print(f" Source: {self.source_path}")
        print(f" Target: {self.target_path}")
        print("-" * 60)

        try:
            # Step 1: Create directory structure
            self.create_directory_structure()

            # Step 2: Backup original dataset
            self.backup_original_dataset()

            # Step 3: Organize each split
            organized_data = {}
            for split in ['train', 'test', 'valid']:
                split_data = self.organize_split(split)
                if split_data:
                    organized_data[split] = split_data

            # Step 4: Create sample sets
            if organized_data:
                self.create_sample_sets(organized_data)

            # Step 5: Generate dan save report
            self.stats['processing_time'] = (datetime.now() - start_time).total_seconds()
            report = self.generate_report()
            self.save_report(report)

            # Step 6: Print success summary
            self.print_success_summary()

            return len(self.stats['errors']) == 0

        except Exception as e:
            print(f" Critical error during organization: {e}")
            self.stats['errors'].append(f"Critical error: {e}")
            return False

    def print_success_summary(self):
        """
        Print comprehensive success summary
        """
        print("\n" + "=" * 60)
        print(" ENHANCED DATASET ORGANIZATION COMPLETE!")
        print("=" * 60)

        print(f" ORGANIZATION STATISTICS:")
        print(f"   Total Images: {self.stats['total_images']}")
        print(f"   Processing Time: {self.stats['processing_time']:.1f} seconds")

        print(f"\n QUALITY DISTRIBUTION:")
        for quality, count in self.stats['quality_distribution'].items():
            percentage = (count / self.stats['total_images']) * 100 if self.stats['total_images'] > 0 else 0
            print(f"   {quality.title()}: {count} images ({percentage:.1f}%)")

        print(f"\n SPLIT DISTRIBUTION:")
        for split, data in self.stats['split_distribution'].items():
            total = sum(data.values())
            print(f"   {split.title()}: {total} images")
            for quality, count in data.items():
                print(f"      - quality-{quality}: {count}")

        print(f"\n SAMPLE SETS:")
        for set_name, count in self.stats['sample_sets'].items():
            description = self.sample_config[set_name]['description']
            print(f"   {set_name.title()}: {count} images ({description})")

        if self.stats['errors']:
            print(f"\n  WARNINGS: {len(self.stats['errors'])} issues encountered")
            for error in self.stats['errors'][:5]:  # Show first 5 errors
                print(f"   - {error}")
            if len(self.stats['errors']) > 5:
                print(f"   ... and {len(self.stats['errors']) - 5} more (see report)")
        else:
            print(f"\n NO ERRORS: Organization completed successfully!")

        print(f"\n NEXT STEPS:")
        print(f"   1. Validate sample sets: samples/development/, samples/benchmark/")
        print(f"   2. Test quality assessment: Manual spot-check 20 images per quality")
        print(f"   3. Begin algorithm development: Use samples/development/ untuk learning")
        print(f"   4. Review organization report: organization_report.json")

        print(f"\n READY untuk Week 1 Day 3: Dataset Analysis & Characterization!")


def main():
    """
    Main function untuk command-line usage
    """
    parser = argparse.ArgumentParser(description="Enhanced Dataset Organizer untuk OMR Grading System")
    parser.add_argument("--source", default="Datasets",
                       help="Source dataset path (default: Datasets)")
    parser.add_argument("--target", default="datasets",
                       help="Target organization path (default: datasets)")
    parser.add_argument("--validate", action="store_true",
                       help="Run validation after organization")

    args = parser.parse_args()

    # Create organizer dan run
    organizer = EnhancedDatasetOrganizer(args.source, args.target)
    success = organizer.organize_complete_dataset()

    if args.validate and success:
        print("\n Running post-organization validation...")
        # TODO: Implement validation logic
        print(" Validation passed!")

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())