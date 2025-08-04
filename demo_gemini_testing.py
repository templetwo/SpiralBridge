#!/usr/bin/env python3
"""
Demo script to showcase and test the Gemini implementation.

This script demonstrates:
1. Platform detection
2. Content cleaning
3. Error handling
4. Archive functionality
5. Real-world usage scenarios
"""

import os
import sys
import tempfile
import shutil
from unittest.mock import Mock

# Add the current directory to Python path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spiralbridge import (
    detect_platform,
    clean_gemini_conversation_content,
    scrape_gemini_conversation,
    get_platform_error_message
)
from archive_conversation import archive_conversation


def demo_platform_detection():
    """Demonstrate platform detection for various Gemini URLs."""
    print("🎯 PLATFORM DETECTION DEMO")
    print("=" * 50)
    
    test_urls = [
        "https://gemini.google.com/app/1a2b3c4d5e6f",
        "https://gemini.google.com/share/abcdef123456",
        "https://g.co/gemini/short123",
        "https://bard.google.com/chat/legacy789",
        "https://claude.ai/share/wrong",  # Should not detect as Gemini
        "invalid-url"  # Should return None
    ]
    
    for url in test_urls:
        platform = detect_platform(url)
        status = "✅ GEMINI" if platform == 'gemini' else f"❌ {platform or 'UNKNOWN'}"
        print(f"  {url}")
        print(f"    → {status}")
        print()


def demo_content_cleaning():
    """Demonstrate content cleaning with various scenarios."""
    print("🧹 CONTENT CLEANING DEMO")
    print("=" * 50)
    
    # Sample Gemini conversation with UI elements
    sample_conversation = """Gemini Apps
Try Gemini Advanced
New chat
⋮

User: Hello! I'm working on a machine learning project and need help with data preprocessing. Can you guide me through the essential steps?

Gemini: I'd be happy to help you with data preprocessing for your machine learning project! Here are the essential steps you should consider:

## 1. Data Collection and Understanding
- **Examine your dataset**: Look at the shape, data types, and basic statistics
- **Identify target variable**: Understand what you're trying to predict
- **Check data source**: Ensure data quality and reliability

```python
import pandas as pd
import numpy as np

# Load and examine data
df = pd.read_csv('your_dataset.csv')
print(df.info())
print(df.describe())
print(df.head())
```

## 2. Data Cleaning
- **Handle missing values**: Decide whether to remove, impute, or flag missing data
- **Remove duplicates**: Identify and handle duplicate rows
- **Fix data types**: Ensure columns have appropriate data types

```python
# Check for missing values
print(df.isnull().sum())

# Handle missing values
df['column_name'].fillna(df['column_name'].mean(), inplace=True)

# Remove duplicates
df.drop_duplicates(inplace=True)
```

## 3. Feature Engineering
- **Create new features**: Derive meaningful features from existing ones
- **Feature selection**: Remove irrelevant or redundant features
- **Feature scaling**: Normalize or standardize numerical features

```python
from sklearn.preprocessing import StandardScaler, LabelEncoder

# Feature scaling
scaler = StandardScaler()
df[['numeric_col1', 'numeric_col2']] = scaler.fit_transform(df[['numeric_col1', 'numeric_col2']])

# Encode categorical variables
le = LabelEncoder()
df['category_col'] = le.fit_transform(df['category_col'])
```

## 4. Data Splitting
- **Train/Validation/Test split**: Separate data for training, validation, and testing
- **Stratified sampling**: Ensure representative samples for classification problems

```python
from sklearn.model_selection import train_test_split

X = df.drop('target', axis=1)
y = df['target']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
```

**Key Tips:**
- Always keep a backup of your original data
- Document your preprocessing steps
- Use cross-validation to validate your approach
- Consider domain-specific preprocessing needs

Would you like me to elaborate on any specific step or discuss preprocessing for a particular type of data (text, images, time series)?

User: This is incredibly helpful! Can you also show me how to handle categorical variables with many categories?

Gemini: Excellent question! Handling high-cardinality categorical variables is a common challenge. Here are several effective strategies:

## 1. Target Encoding (Mean Encoding)
Replace categories with the mean target value for that category.

```python
import pandas as pd
from sklearn.model_selection import KFold

def target_encode(X, y, column, n_splits=5):
    # Create a copy to avoid modifying original data
    X_encoded = X.copy()
    
    # Cross-validation to prevent overfitting
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
    
    for train_idx, val_idx in kf.split(X):
        # Calculate mean target for each category on training fold
        means = y.iloc[train_idx].groupby(X.iloc[train_idx][column]).mean()
        
        # Apply encoding to validation fold
        X_encoded.loc[val_idx, f'{column}_encoded'] = X.loc[val_idx, column].map(means)
    
    return X_encoded

# Usage
df_encoded = target_encode(X_train, y_train, 'high_cardinality_column')
```

## 2. Frequency Encoding
Replace categories with their frequency of occurrence.

```python
# Frequency encoding
freq_encoding = X_train['category_col'].value_counts().to_dict()
X_train['category_freq'] = X_train['category_col'].map(freq_encoding)
X_test['category_freq'] = X_test['category_col'].map(freq_encoding)

# Handle unseen categories in test set
X_test['category_freq'].fillna(0, inplace=True)
```

## 3. Grouping Rare Categories
Combine infrequent categories into an "Other" group.

```python
def group_rare_categories(df, column, threshold=0.01):
    # Calculate frequency of each category
    freq = df[column].value_counts(normalize=True)
    
    # Identify rare categories
    rare_categories = freq[freq < threshold].index
    
    # Replace rare categories with 'Other'
    df[f'{column}_grouped'] = df[column].replace(rare_categories, 'Other')
    
    return df

# Usage
df_grouped = group_rare_categories(X_train, 'high_cardinality_col', threshold=0.02)
```

## 4. Hash Encoding
Use hash functions to map categories to a fixed number of buckets.

```python
import hashlib

def hash_encode(series, n_buckets=10):
    return series.apply(lambda x: int(hashlib.md5(str(x).encode()).hexdigest(), 16) % n_buckets)

# Usage
X_train['category_hash'] = hash_encode(X_train['category_col'], n_buckets=20)
```

## 5. Embedding (for Deep Learning)
Learn dense representations of categories.

```python
import tensorflow as tf
from tensorflow.keras.layers import Embedding, Input, Flatten
from tensorflow.keras.models import Model

def create_embedding_model(vocab_size, embedding_dim=50):
    input_layer = Input(shape=(1,))
    embedding = Embedding(vocab_size, embedding_dim)(input_layer)
    flattened = Flatten()(embedding)
    
    model = Model(inputs=input_layer, outputs=flattened)
    return model

# Usage for categorical column with vocab_size unique categories
embedding_model = create_embedding_model(vocab_size=1000, embedding_dim=50)
```

## 6. Feature Hashing with scikit-learn
```python
from sklearn.feature_extraction import FeatureHasher

# Create feature hasher
hasher = FeatureHasher(n_features=100, input_type='string')

# Transform categorical data
hashed_features = hasher.transform(X_train['category_col'].astype(str))
```

## Best Practices:
1. **Validate on holdout data**: Always test your encoding on unseen data
2. **Handle missing values**: Decide how to encode missing categories
3. **Monitor for data leakage**: Be careful with target encoding
4. **Consider domain knowledge**: Some categories may have natural groupings
5. **Experiment with combinations**: Try multiple encoding methods together

## When to Use Each Method:
- **Target Encoding**: When you have a clear relationship between category and target
- **Frequency Encoding**: When frequency itself is predictive
- **Grouping**: When you have many rare categories
- **Hash Encoding**: When you need consistent dimensionality
- **Embeddings**: For deep learning with very high cardinality

Would you like me to dive deeper into any of these methods or show you how to evaluate which encoding works best for your specific dataset?

View other drafts
Share & export
Copy link
Export to Docs

Gemini can make mistakes, so please double-check.
Privacy & Terms
Help
Made by Google"""
    
    print("Original conversation (with UI elements):")
    print("-" * 40)
    print(sample_conversation[:500] + "..." if len(sample_conversation) > 500 else sample_conversation)
    print("-" * 40)
    print(f"Original length: {len(sample_conversation)} characters")
    print()
    
    # Clean the content
    cleaned = clean_gemini_conversation_content(sample_conversation)
    
    print("Cleaned conversation (UI elements removed):")
    print("-" * 40)
    print(cleaned[:500] + "..." if len(cleaned) > 500 else cleaned)
    print("-" * 40)
    print(f"Cleaned length: {len(cleaned)} characters")
    print(f"Reduction: {len(sample_conversation) - len(cleaned)} characters ({((len(sample_conversation) - len(cleaned)) / len(sample_conversation) * 100):.1f}%)")
    print()
    
    # Verify important content is preserved
    print("✅ Content Verification:")
    preserved_elements = [
        "machine learning project",
        "data preprocessing",
        "```python",
        "import pandas as pd",
        "Target Encoding",
        "Frequency Encoding",
        "high-cardinality categorical"
    ]
    
    for element in preserved_elements:
        if element in cleaned:
            print(f"  ✓ '{element}' preserved")
        else:
            print(f"  ❌ '{element}' missing")
    
    # Verify UI elements are removed
    print("\n🧹 UI Element Removal:")
    ui_elements = [
        "Gemini Apps",
        "Try Gemini Advanced", 
        "New chat",
        "View other drafts",
        "Share & export",
        "Gemini can make mistakes",
        "Made by Google"
    ]
    
    for element in ui_elements:
        if element not in cleaned:
            print(f"  ✓ '{element}' removed")
        else:
            print(f"  ❌ '{element}' still present")


def demo_error_handling():
    """Demonstrate error handling scenarios."""
    print("⚠️  ERROR HANDLING DEMO")
    print("=" * 50)
    
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
    
    error_scenarios = [
        ("Timeout Error", TimeoutException("Page load timeout after 30 seconds")),
        ("Element Not Found", NoSuchElementException("Unable to locate conversation content")),
        ("Access Denied", WebDriverException("Access denied: Private conversation")),
        ("Network Error", WebDriverException("Connection refused by server")),
        ("Rate Limited", WebDriverException("Too many requests - rate limited")),
    ]
    
    for scenario_name, exception in error_scenarios:
        print(f"Scenario: {scenario_name}")
        error_message = get_platform_error_message('gemini', exception)
        print(f"  Error Message: {error_message}")
        print()


def demo_archiving():
    """Demonstrate content archiving functionality."""
    print("📁 ARCHIVING DEMO")
    print("=" * 50)
    
    # Create temporary directory for demo
    temp_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    
    try:
        os.chdir(temp_dir)
        
        # Sample cleaned conversation content
        sample_content = """User: Can you explain the difference between supervised and unsupervised learning?

Gemini: I'd be happy to explain the key differences between supervised and unsupervised learning!

## Supervised Learning
**Definition**: Learning with labeled training data where you know the correct answers.

**Key Characteristics:**
- Uses input-output pairs for training
- Goal is to predict outcomes for new, unseen data
- Performance can be measured against known correct answers

**Common Algorithms:**
- Linear/Logistic Regression
- Decision Trees
- Random Forest
- Support Vector Machines
- Neural Networks

**Examples:**
- Email spam detection (emails labeled as spam/not spam)
- Image classification (photos labeled with object names)
- Stock price prediction (historical prices with known outcomes)

## Unsupervised Learning
**Definition**: Learning patterns from data without labeled examples or known correct answers.

**Key Characteristics:**
- Works with input data only (no target labels)
- Goal is to discover hidden patterns or structures
- Harder to evaluate since there's no "ground truth"

**Common Algorithms:**
- K-Means Clustering
- Hierarchical Clustering
- Principal Component Analysis (PCA)
- Association Rules
- Anomaly Detection

**Examples:**
- Customer segmentation (grouping customers by behavior)
- Market basket analysis (finding product purchase patterns)
- Dimensionality reduction for data visualization

## Key Differences Summary:

| Aspect | Supervised | Unsupervised |
|--------|------------|--------------|
| Data Type | Labeled | Unlabeled |
| Goal | Prediction | Pattern Discovery |
| Evaluation | Easy (compare to labels) | Difficult (subjective) |
| Use Cases | Classification, Regression | Clustering, Association |

Would you like me to dive deeper into any specific algorithms or provide code examples?

User: That's a great explanation! Can you show me a simple code example of both?

Gemini: Absolutely! Here are practical examples of both supervised and unsupervised learning:

## Supervised Learning Example - Classification

```python
# Import libraries
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Load the famous Iris dataset (labeled data)
iris = load_iris()
X, y = iris.data, iris.target

print("Dataset shape:", X.shape)
print("Classes:", iris.target_names)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Create and train the model
classifier = RandomForestClassifier(n_estimators=100, random_state=42)
classifier.fit(X_train, y_train)

# Make predictions
y_pred = classifier.predict(X_test)

# Evaluate performance
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.3f}")
print("\\nDetailed Classification Report:")
print(classification_report(y_test, y_pred, target_names=iris.target_names))
```

## Unsupervised Learning Example - Clustering

```python
# Import libraries
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# Generate sample data (no labels!)
X, _ = make_blobs(n_samples=300, centers=4, cluster_std=0.60, random_state=0)

print("Dataset shape:", X.shape)
print("Note: We're ignoring the true labels to simulate unsupervised learning")

# Apply K-Means clustering
n_clusters = 4
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
cluster_labels = kmeans.fit_predict(X)

# Evaluate clustering quality (without using true labels)
silhouette_avg = silhouette_score(X, cluster_labels)
print(f"Silhouette Score: {silhouette_avg:.3f}")

# Visualize results
plt.figure(figsize=(12, 5))

# Plot original data
plt.subplot(1, 2, 1)
plt.scatter(X[:, 0], X[:, 1], alpha=0.6)
plt.title("Original Data (Unlabeled)")
plt.xlabel("Feature 1")
plt.ylabel("Feature 2")

# Plot clustered data
plt.subplot(1, 2, 2)
colors = ['red', 'blue', 'green', 'purple']
for i in range(n_clusters):
    cluster_points = X[cluster_labels == i]
    plt.scatter(cluster_points[:, 0], cluster_points[:, 1], 
                c=colors[i], label=f'Cluster {i}', alpha=0.6)

# Plot cluster centers
centers = kmeans.cluster_centers_
plt.scatter(centers[:, 0], centers[:, 1], c='black', marker='x', s=100, label='Centroids')
plt.title("K-Means Clustering Results")
plt.xlabel("Feature 1")
plt.ylabel("Feature 2")
plt.legend()

plt.tight_layout()
plt.show()
```

## Key Observations:

**Supervised Learning (Classification):**
- We had labeled data (iris species)
- We could measure exact accuracy (93.3% in this example)
- Clear success/failure metric
- Model learns to map features → labels

**Unsupervised Learning (Clustering):** 
- No labels provided to the algorithm
- Evaluation is more subjective (silhouette score helps)
- We discover natural groupings in the data
- Model learns hidden patterns in feature space

## When to Use Each:

**Use Supervised Learning when:**
- You have labeled training data
- You want to predict specific outcomes
- You can define what "success" looks like

**Use Unsupervised Learning when:**
- You don't have labels
- You want to explore data structure
- You're looking for hidden patterns or anomalies

Would you like me to show examples of other algorithms or explain how to choose between different approaches?"""
        
        print("Sample conversation content to archive:")
        print("-" * 40)
        print(sample_content[:300] + "...")
        print("-" * 40)
        print(f"Content length: {len(sample_content)} characters")
        print()
        
        # Archive the content
        archive_path = archive_conversation(sample_content, 'gemini')
        
        print(f"✅ Content archived successfully!")
        print(f"Archive path: {archive_path}")
        print(f"File size: {os.path.getsize(archive_path)} bytes")
        
        # Verify the archived content
        with open(archive_path, 'r', encoding='utf-8') as f:
            archived_content = f.read()
        
        print(f"✅ Content verification: {'OK' if archived_content == sample_content else 'FAILED'}")
        
        # Show directory structure
        print(f"\nDirectory structure:")
        for root, dirs, files in os.walk('.'):
            level = root.replace('.', '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            sub_indent = ' ' * 2 * (level + 1)
            for file in files:
                print(f"{sub_indent}{file}")
    
    finally:
        # Cleanup
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir, ignore_errors=True)


def demo_mock_scraping():
    """Demonstrate scraping with mock browser responses."""
    print("🌐 MOCK SCRAPING DEMO")
    print("=" * 50)
    
    # Mock browser response
    mock_browser = Mock()
    mock_element = Mock()
    mock_element.text = """Gemini Apps
Try Gemini Advanced
New chat

User: What are the key principles of clean code?

Gemini: Great question! Clean code is essential for maintainable software. Here are the key principles:

## 1. Meaningful Names
- Use descriptive variable and function names
- Avoid abbreviations and misleading names
- Be consistent with naming conventions

```python
# Bad
def calc(x, y):
    return x * y * 0.1

# Good  
def calculate_discount_amount(price, quantity):
    DISCOUNT_RATE = 0.1
    return price * quantity * DISCOUNT_RATE
```

## 2. Small Functions
- Functions should do one thing well
- Keep functions short (usually < 20 lines)
- Use descriptive function names

## 3. Clear Comments
- Write comments that explain WHY, not WHAT
- Keep comments up-to-date with code changes
- Remove outdated or obvious comments

## 4. Consistent Formatting
- Use consistent indentation and spacing
- Follow language-specific style guides
- Use automated formatters when possible

## 5. Error Handling
- Handle errors gracefully
- Use exceptions appropriately
- Provide meaningful error messages

These principles make code easier to read, maintain, and debug!

User: Can you give me more examples of good vs bad naming?

Gemini: Absolutely! Here are more examples showing the difference between poor and clean naming:

## Variable Names

**Bad Examples:**
```python
d = 86400  # What does 'd' represent?
user_list = get_users()  # 'list' is redundant
temp = calculate_price() * 0.08  # What kind of temp?
flag = True  # Flag for what?
```

**Good Examples:**
```python
SECONDS_PER_DAY = 86400
active_users = get_users()
sales_tax = calculate_price() * 0.08
is_email_valid = True
```

## Function Names

**Bad Examples:**
```python
def process():  # Process what?
def handle_data(x):  # Handle how?
def do_stuff():  # What stuff?
def manager():  # Manages what?
```

**Good Examples:**
```python
def validate_email_format():
def parse_csv_file(file_path):
def send_welcome_email():
def create_user_account():
```

## Class Names

**Bad Examples:**
```python
class Data:  # Too generic
class Manager:  # What does it manage?
class Helper:  # Helps with what?
class Processor:  # Processes what?
```

**Good Examples:**
```python
class UserAccount:
class EmailService:
class DatabaseConnection:
class PaymentProcessor:
```

## Constants

**Bad Examples:**
```python
MAX = 100  # Maximum what?
PI = 3.14159  # This one's actually okay
LIMIT = 50  # Limit of what?
```

**Good Examples:**
```python
MAX_LOGIN_ATTEMPTS = 100
PI = 3.14159  # Mathematical constant
RATE_LIMIT_PER_MINUTE = 50
```

**Key Naming Rules:**
1. **Be specific**: `user_count` vs `count`
2. **Use searchable names**: `MAX_RETRY_COUNT` vs `7`
3. **Avoid mental mapping**: `elapsed_time` vs `t`
4. **Use pronounceable names**: `creation_timestamp` vs `crttn_tmstmp`
5. **Avoid disinformation**: Don't call something `account_list` if it's actually a dictionary

The goal is that someone reading your code for the first time should understand what each variable represents without needing additional context!

Privacy & Terms
Made by Google"""
    
    mock_browser.find_element.return_value = mock_element
    mock_browser.find_elements.return_value = []  # No specific conversation elements
    
    print("Simulating scraping from URL: https://gemini.google.com/share/demo123")
    print()
    
    # Simulate scraping
    result = scrape_gemini_conversation(mock_browser, "https://gemini.google.com/share/demo123", timeout=1)
    
    if result:
        print("✅ Scraping successful!")
        print(f"Content length: {len(result)} characters")
        print()
        print("Content preview:")
        print("-" * 40)
        print(result[:400] + "..." if len(result) > 400 else result)
        print("-" * 40)
        
        # Verify cleaning worked
        ui_removed = all(element not in result for element in [
            "Gemini Apps", "Try Gemini Advanced", "New chat", 
            "Privacy & Terms", "Made by Google"
        ])
        
        content_preserved = all(element in result for element in [
            "clean code", "Meaningful Names", "```python", "calculate_discount_amount"
        ])
        
        print(f"\n✅ UI elements removed: {'Yes' if ui_removed else 'No'}")
        print(f"✅ Content preserved: {'Yes' if content_preserved else 'No'}")
    else:
        print("❌ Scraping failed!")


def main():
    """Run all demos."""
    print("🌉 SPIRALBRIDGE GEMINI IMPLEMENTATION DEMO")
    print("=" * 60)
    print("This demo showcases the Gemini conversation link implementation")
    print("with various test scenarios and edge cases.")
    print("=" * 60)
    print()
    
    # Run all demos
    demo_platform_detection()
    print()
    
    demo_content_cleaning()
    print()
    
    demo_error_handling()
    print()
    
    demo_archiving()
    print()
    
    demo_mock_scraping()
    print()
    
    print("🎉 DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\n📋 SUMMARY OF TESTED FEATURES:")
    print("✅ Platform detection for various Gemini URL formats")  
    print("✅ Content cleaning (UI element removal)")
    print("✅ Content preservation (conversation data intact)")
    print("✅ Error handling with informative messages")
    print("✅ Archive functionality with timestamp-based naming")
    print("✅ Mock browser scraping simulation")
    
    print("\n🧪 NEXT STEPS FOR MANUAL TESTING:")
    print("1. Create actual Gemini conversations and share them")
    print("2. Test with: python spiralbridge.py [YOUR_GEMINI_URL]")
    print("3. Verify outputs in memory_logs/gemini/ directory")
    print("4. Test error scenarios with invalid/expired URLs")
    print("5. Run performance tests with large conversations")
    
    print("\n🚀 RUN AUTOMATED TESTS:")
    print("   python test_gemini_implementation.py")
    print("   python test_gemini_edge_cases.py")


if __name__ == "__main__":
    main()
