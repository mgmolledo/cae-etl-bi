"""
CAE ETL Pipeline - Professional Implementation
Advanced ETL pipeline for CAE (Coordinación de Actividades Empresariales) analysis
"""

import os
import logging
import pandas as pd
import numpy as np
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import hashlib
import json
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class DataSource:
    """Data source configuration"""
    name: str
    url: str
    file_type: str
    expected_size_mb: float
    validation_checksum: Optional[str] = None
    last_updated: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3

class CAEETLPipeline:
    """
    Professional ETL Pipeline for CAE Analysis
    Handles data extraction, validation, transformation, and loading
    """
    
    def __init__(self, base_dir: str = "data"):
        self.base_dir = Path(base_dir)
        self.raw_dir = self.base_dir / "raw"
        self.processed_dir = self.base_dir / "processed"
        self.logs_dir = self.base_dir / "logs"
        
        # Create directories
        for dir_path in [self.raw_dir, self.processed_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize data sources
        self.data_sources = self._initialize_data_sources()
        
        # Pipeline metrics
        self.pipeline_metrics = {
            'start_time': None,
            'end_time': None,
            'total_records': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'data_quality_score': 0.0
        }
    
    def _initialize_data_sources(self) -> Dict[str, DataSource]:
        """Initialize data sources with professional configuration"""
        return {
            "boe_rd171": DataSource(
                name="BOE RD 171/2004",
                url="https://www.boe.es/buscar/pdf/2004/BOE-A-2004-1848-consolidado.pdf",
                file_type="pdf",
                expected_size_mb=2.5,
                last_updated=datetime(2004, 1, 30)
            ),
            "insst_criterios": DataSource(
                name="INSST Criterios Técnicos",
                url="https://www.insst.es/documents/94886/627464/Directrices_ITSS.pdf",
                file_type="pdf",
                expected_size_mb=1.8,
                last_updated=datetime(2023, 6, 15)
            ),
            "itss_directrices": DataSource(
                name="ITSS Directrices",
                url="https://www.insst.es/documents/94886/627464/Directrices_ITSS.pdf",
                file_type="pdf",
                expected_size_mb=1.2,
                last_updated=datetime(2023, 8, 20)
            ),
            "flc_tpc_data": DataSource(
                name="FLC TPC Data",
                url="https://www.fundacionlaboral.org/estadisticas/",
                file_type="csv",
                expected_size_mb=0.5,
                last_updated=datetime(2024, 1, 10)
            ),
            "civismo_cargas": DataSource(
                name="Civismo Cargas Administrativas",
                url="https://www.civismo.org/informes/cargas-administrativas/",
                file_type="xlsx",
                expected_size_mb=3.2,
                last_updated=datetime(2024, 2, 15)
            )
        }
    
    def extract_data(self, parallel: bool = True) -> Dict[str, bool]:
        """
        Extract data from all sources with professional error handling
        
        Args:
            parallel: Whether to use parallel processing
            
        Returns:
            Dictionary with extraction results
        """
        logger.info("Starting data extraction phase")
        self.pipeline_metrics['start_time'] = datetime.now()
        
        extraction_results = {}
        
        if parallel:
            extraction_results = self._extract_parallel()
        else:
            extraction_results = self._extract_sequential()
        
        self.pipeline_metrics['successful_extractions'] = sum(extraction_results.values())
        self.pipeline_metrics['failed_extractions'] = len(extraction_results) - sum(extraction_results.values())
        
        logger.info(f"Extraction completed: {self.pipeline_metrics['successful_extractions']} successful, "
                   f"{self.pipeline_metrics['failed_extractions']} failed")
        
        return extraction_results
    
    def _extract_parallel(self) -> Dict[str, bool]:
        """Extract data using parallel processing"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_source = {
                executor.submit(self._extract_single_source, name, source): name 
                for name, source in self.data_sources.items()
            }
            
            for future in as_completed(future_to_source):
                source_name = future_to_source[future]
                try:
                    results[source_name] = future.result()
                except Exception as e:
                    logger.error(f"Error in parallel extraction for {source_name}: {e}")
                    results[source_name] = False
        
        return results
    
    def _extract_sequential(self) -> Dict[str, bool]:
        """Extract data sequentially"""
        results = {}
        
        for name, source in self.data_sources.items():
            results[name] = self._extract_single_source(name, source)
        
        return results
    
    def _extract_single_source(self, name: str, source: DataSource) -> bool:
        """
        Extract data from a single source with retry logic
        
        Args:
            name: Source name
            source: DataSource configuration
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Extracting data from {source.name}")
        
        for attempt in range(source.max_retries):
            try:
                # Download data
                response = requests.get(
                    source.url,
                    headers={
                        "User-Agent": "CAE-ETL-Pipeline/1.0 (Professional Data Analysis)",
                        "Accept": "application/pdf,application/vnd.ms-excel,text/csv,*/*"
                    },
                    timeout=30,
                    stream=True
                )
                response.raise_for_status()
                
                # Validate file size
                content_length = response.headers.get('content-length')
                if content_length:
                    size_mb = int(content_length) / (1024 * 1024)
                    if size_mb > source.expected_size_mb * 2:
                        logger.warning(f"File size {size_mb:.2f}MB exceeds expected {source.expected_size_mb}MB")
                
                # Save file
                file_path = self.raw_dir / f"{name}.{source.file_type}"
                with open(file_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Validate file
                if self._validate_extracted_file(file_path, source):
                    logger.info(f"Successfully extracted {source.name}")
                    return True
                else:
                    logger.error(f"Validation failed for {source.name}")
                    file_path.unlink(missing_ok=True)
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error for {source.name} (attempt {attempt + 1}): {e}")
            except Exception as e:
                logger.error(f"Unexpected error for {source.name} (attempt {attempt + 1}): {e}")
            
            if attempt < source.max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.info(f"Retrying {source.name} in {wait_time} seconds...")
                time.sleep(wait_time)
        
        logger.error(f"Failed to extract {source.name} after {source.max_retries} attempts")
        return False
    
    def _validate_extracted_file(self, file_path: Path, source: DataSource) -> bool:
        """
        Validate extracted file
        
        Args:
            file_path: Path to the extracted file
            source: DataSource configuration
            
        Returns:
            True if validation passes
        """
        try:
            # Check if file exists and has content
            if not file_path.exists() or file_path.stat().st_size == 0:
                return False
            
            # Check file size
            size_mb = file_path.stat().st_size / (1024 * 1024)
            if size_mb < source.expected_size_mb * 0.1:  # At least 10% of expected size
                logger.warning(f"File {file_path.name} is too small: {size_mb:.2f}MB")
                return False
            
            # Calculate checksum for integrity
            checksum = self._calculate_checksum(file_path)
            
            # Save metadata
            metadata = {
                'source_name': source.name,
                'extraction_time': datetime.now().isoformat(),
                'file_size_mb': size_mb,
                'checksum': checksum,
                'url': source.url
            }
            
            metadata_path = file_path.with_suffix('.metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return True
            
        except Exception as e:
            logger.error(f"Validation error for {file_path}: {e}")
            return False
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum for file integrity"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def transform_data(self) -> Dict[str, pd.DataFrame]:
        """
        Transform raw data into analysis-ready format
        
        Returns:
            Dictionary of transformed DataFrames
        """
        logger.info("Starting data transformation phase")
        
        transformed_data = {}
        
        # Process each extracted file
        for file_path in self.raw_dir.glob("*"):
            if file_path.suffix in ['.csv', '.xlsx', '.json']:
                try:
                    df = self._load_and_transform_file(file_path)
                    if df is not None and not df.empty:
                        transformed_data[file_path.stem] = df
                        logger.info(f"Transformed {file_path.name}: {len(df)} records")
                except Exception as e:
                    logger.error(f"Error transforming {file_path.name}: {e}")
        
        # Generate synthetic CAE data for analysis
        synthetic_data = self._generate_synthetic_cae_data()
        transformed_data['synthetic_cae_data'] = synthetic_data
        
        self.pipeline_metrics['total_records'] = sum(len(df) for df in transformed_data.values())
        
        logger.info(f"Transformation completed: {len(transformed_data)} datasets, "
                   f"{self.pipeline_metrics['total_records']} total records")
        
        return transformed_data
    
    def _load_and_transform_file(self, file_path: Path) -> Optional[pd.DataFrame]:
        """Load and transform a single file"""
        try:
            if file_path.suffix == '.csv':
                df = pd.read_csv(file_path, encoding='utf-8')
            elif file_path.suffix == '.xlsx':
                df = pd.read_excel(file_path)
            elif file_path.suffix == '.json':
                df = pd.read_json(file_path)
            else:
                return None
            
            # Basic data cleaning
            df = df.dropna(how='all')  # Remove completely empty rows
            df = df.drop_duplicates()  # Remove duplicates
            
            # Standardize column names
            df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('-', '_')
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return None
    
    def _generate_synthetic_cae_data(self) -> pd.DataFrame:
        """Generate synthetic CAE data for analysis"""
        np.random.seed(42)
        
        n_companies = 5000
        n_years = 5
        
        data = []
        
        for year in range(2020, 2025):
            for company_id in range(n_companies):
                # Company characteristics
                company_size = np.random.choice(['micro', 'pequeña', 'mediana', 'grande'], 
                                              p=[0.6, 0.25, 0.12, 0.03])
                
                # CAE-related metrics
                cae_procedures = np.random.poisson(3) if company_size in ['micro', 'pequeña'] else np.random.poisson(8)
                administrative_cost = np.random.normal(5000, 2000) if company_size == 'micro' else np.random.normal(15000, 5000)
                processing_time_days = np.random.normal(45, 15)
                
                # Inefficiency indicators
                inefficiency_score = np.random.beta(2, 5)  # Skewed towards lower inefficiency
                if company_size == 'micro':
                    inefficiency_score += 0.2  # Micro companies face more inefficiencies
                
                # Geographic factors
                region = np.random.choice(['Madrid', 'Cataluña', 'Andalucía', 'Valencia', 'País Vasco', 'Otras'])
                if region in ['Madrid', 'Cataluña']:
                    processing_time_days *= 0.8  # More efficient regions
                
                data.append({
                    'company_id': f"COMP_{company_id:04d}",
                    'year': year,
                    'company_size': company_size,
                    'region': region,
                    'cae_procedures': max(0, cae_procedures),
                    'administrative_cost_eur': max(0, administrative_cost),
                    'processing_time_days': max(1, processing_time_days),
                    'inefficiency_score': min(1.0, inefficiency_score),
                    'sector': np.random.choice(['Construcción', 'Servicios', 'Industria', 'Comercio']),
                    'employees': np.random.randint(1, 500) if company_size == 'micro' else np.random.randint(500, 5000),
                    'annual_revenue_eur': np.random.randint(100000, 10000000),
                    'cae_compliance_rate': np.random.beta(8, 2),  # High compliance rate
                    'bureaucratic_burden_score': np.random.beta(3, 7)  # Low burden
                })
        
        return pd.DataFrame(data)
    
    def load_data(self, transformed_data: Dict[str, pd.DataFrame]) -> None:
        """
        Load transformed data to processed directory
        
        Args:
            transformed_data: Dictionary of transformed DataFrames
        """
        logger.info("Starting data loading phase")
        
        for name, df in transformed_data.items():
            try:
                # Save as parquet for efficiency
                output_path = self.processed_dir / f"{name}.parquet"
                df.to_parquet(output_path, index=False)
                
                # Also save as CSV for compatibility
                csv_path = self.processed_dir / f"{name}.csv"
                df.to_csv(csv_path, index=False)
                
                logger.info(f"Loaded {name}: {len(df)} records to {output_path}")
                
            except Exception as e:
                logger.error(f"Error loading {name}: {e}")
        
        # Calculate data quality score
        self.pipeline_metrics['data_quality_score'] = self._calculate_data_quality_score(transformed_data)
        
        self.pipeline_metrics['end_time'] = datetime.now()
        duration = self.pipeline_metrics['end_time'] - self.pipeline_metrics['start_time']
        
        logger.info(f"ETL Pipeline completed in {duration.total_seconds():.2f} seconds")
        logger.info(f"Data quality score: {self.pipeline_metrics['data_quality_score']:.2f}")
    
    def _calculate_data_quality_score(self, data: Dict[str, pd.DataFrame]) -> float:
        """Calculate overall data quality score"""
        if not data:
            return 0.0
        
        quality_scores = []
        
        for name, df in data.items():
            # Completeness score
            completeness = 1 - (df.isnull().sum().sum() / (len(df) * len(df.columns)))
            
            # Consistency score (no duplicates)
            consistency = 1 - (df.duplicated().sum() / len(df))
            
            # Validity score (basic data type validation)
            validity = 1.0  # Simplified for now
            
            # Overall score for this dataset
            dataset_score = (completeness + consistency + validity) / 3
            quality_scores.append(dataset_score)
        
        return np.mean(quality_scores)
    
    def get_pipeline_summary(self) -> Dict:
        """Get comprehensive pipeline summary"""
        duration = None
        if self.pipeline_metrics['start_time'] and self.pipeline_metrics['end_time']:
            duration = (self.pipeline_metrics['end_time'] - self.pipeline_metrics['start_time']).total_seconds()
        
        return {
            'pipeline_metrics': self.pipeline_metrics,
            'duration_seconds': duration,
            'data_sources_count': len(self.data_sources),
            'success_rate': (
                self.pipeline_metrics['successful_extractions'] / 
                (self.pipeline_metrics['successful_extractions'] + self.pipeline_metrics['failed_extractions'])
                if (self.pipeline_metrics['successful_extractions'] + self.pipeline_metrics['failed_extractions']) > 0 
                else 0
            ),
            'data_quality_score': self.pipeline_metrics['data_quality_score']
        }

def main():
    """Main ETL pipeline execution"""
    logger.info("Starting CAE ETL Pipeline")
    
    # Initialize pipeline
    pipeline = CAEETLPipeline()
    
    try:
        # Extract data
        extraction_results = pipeline.extract_data(parallel=True)
        
        # Transform data
        transformed_data = pipeline.transform_data()
        
        # Load data
        pipeline.load_data(transformed_data)
        
        # Get summary
        summary = pipeline.get_pipeline_summary()
        
        logger.info("ETL Pipeline completed successfully")
        logger.info(f"Summary: {summary}")
        
        return True
        
    except Exception as e:
        logger.error(f"ETL Pipeline failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
