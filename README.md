# 📊 HR Analytics Project

## 🎯 Project Overview

A comprehensive data analytics project focused on analyzing human resources data and predicting employee attrition. This project combines data analysis and machine learning techniques to extract valuable insights that help HR management make data-driven decisions.

**🔗 Cloud Integration**: This project is integrated with **Databricks** for cloud-based data processing. All outputs (models, reports, and visualizations) are stored and managed in Databricks.

## 📋 Key Objectives

- **Predict Employee Attrition**: Build predictive models to identify employees at risk of leaving
- **Performance Analysis**: Measure and analyze various employee performance metrics
- **Employee Segmentation**: Group employees into similar clusters (Clustering)
- **Extract Insights**: Discover patterns and factors affecting employee attrition
- **Decision Support**: Provide interactive dashboards for easy decision-making

## 📁 Project Structure

```
hrAnalysis-cloudData/
│
├── README.md                         # Project documentation
├── requirements.txt                  # Required Python packages
├── main.py                           # Main entry point to run the entire pipeline
│
├── data/
│   ├── raw/
│   │   └── WA_Fn-UseC_-HR-Employee-Attrition.csv  # Raw data
│   └── processed/                    # Cleaned and processed data
│
├── src/                              # Main project library
│   ├── __init__.py
│   ├── config.py                     # Configuration, constants, and paths
│   ├── preprocessing.py              # Data cleaning and preparation
│   ├── eda.py                        # Exploratory Data Analysis (EDA)
│   ├── features.py                   # Feature Engineering
│   ├── attrition_model.py            # Employee Attrition Prediction Model
│   ├── performance_model.py          # Performance Evaluation Model
│   ├── clustering.py                 # Clustering Analysis
│   └── insights.py                   # Insights and Reports Generation
│
├── dashboard/                        # Interactive Dashboards
│   └── HR_Analytics.pbix             # Power BI Dashboard
│
├── figures/                          # Visualizations and Charts
├── models/                           # Trained and Saved Models
├── reports/                          # Generated Reports and Results
├── docs/                             # Additional Documentation
│   ├── final_report.pdf              # Final Project Report
│   └── presentation.pptx             # Presentation Slides
└── labs/                             # Experiments and Testing Files
```

## 🛠️ Technologies and Libraries Used

- **Python 3.8+**: Core programming language
- **Pandas**: Data manipulation and analysis
- **NumPy**: Advanced numerical operations
- **Scikit-learn**: Machine learning models
- **Matplotlib & Seaborn**: Data visualizations
- **Power BI**: Interactive dashboards
- **Databricks**: Cloud platform for data processing and storage

## ☁️ Databricks Integration

This project leverages **Databricks** as the primary cloud platform for:
- **Data Processing**: Distributed data processing and transformation
- **Model Training**: Training machine learning models at scale
- **Output Storage**: All generated models, reports, and visualizations are stored in Databricks
- **Collaboration**: Cloud-based environment for team collaboration

### Output Location
All project outputs are automatically generated and stored in Databricks:
- 📊 Trained models and artifacts
- 📈 Generated reports and analytics
- 📋 Processed datasets
- 📉 Visualizations and charts

## 📊 Dataset Used

The project uses the HR Employee Attrition dataset which includes:
- Employee information (age, salary, job title, etc.)
- Performance and job satisfaction metrics
- Employee attrition status (left or stayed)

## 🚀 How to Run the Project

### Installation Requirements

```bash
# Install required packages
pip install -r requirements.txt
```

### Run the Complete Pipeline

```bash
# Run the entire project
python main.py
```

> **Note**: When running in Databricks, outputs are automatically saved to your Databricks workspace. Check the Databricks ML Registry and workspace folders for generated artifacts.

## 📂 Accessing Outputs in Databricks

After running the pipeline, find your outputs:
1. **Models**: Check MLflow Registry or `/Users/[username]/models/`
2. **Reports**: Available in `/Workspace/[project-path]/reports/`
3. **Processed Data**: Stored in Databricks Tables or Delta Lake
4. **Visualizations**: Accessible through Databricks Notebooks

## 📈 Project Outputs

All project outputs are generated and stored in **Databricks**:

1. **Predictive Models**:
   - Employee Attrition Prediction Model (saved in Databricks MLflow)
   - Performance Evaluation Model (saved in Databricks MLflow)

2. **Reports and Analysis**:
   - List of high-risk employees
   - Employee segmentation into personas
   - Key insights and recommendations
   - CSV exports available in Databricks workspace

3. **Interactive Dashboards**:
   - Power BI dashboard for data visualization and results
   - Databricks SQL analytics for real-time monitoring

4. **Processed Data**:
   - Cleaned and feature-engineered datasets
   - Model predictions and scores

## 👥 Project Team

A collaborative project by Computer Science Year 2, Semester 2 students

## 📝 License and Notes

This project is for educational and analytical purposes.

---

**Last Updated**: May 2026
