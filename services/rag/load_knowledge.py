"""Load sample medical knowledge into Qdrant."""
from services.rag.vector_store import get_knowledge_store


# Sample radiology knowledge
RADIOLOGY_KNOWLEDGE = [
    {
        "text": "Normal chest X-ray findings include clear lung fields without infiltrates, consolidation, or effusion. The cardiac silhouette should be within normal limits. No pneumothorax should be present.",
        "metadata": {
            "source": "Radiology Guidelines",
            "category": "chest_xray",
            "modality": "xray",
            "topic": "normal_findings"
        }
    },
    {
        "text": "Pneumonia typically presents with focal consolidation or infiltrates in the lung parenchyma. Associated findings may include air bronchograms, pleural effusion, and increased opacity.",
        "metadata": {
            "source": "Radiology Atlas",
            "category": "chest_xray",
            "modality": "xray",
            "topic": "pneumonia"
        }
    },
    {
        "text": "Pneumothorax is characterized by the presence of air in the pleural space, visible as a lucent area without lung markings peripheral to the visceral pleural line.",
        "metadata": {
            "source": "Emergency Radiology",
            "category": "chest_xray",
            "modality": "xray",
            "topic": "pneumothorax"
        }
    },
    {
        "text": "Cardiomegaly is defined as a cardiothoracic ratio greater than 0.5 on a PA chest radiograph. It may indicate heart failure, valvular disease, or cardiomyopathy.",
        "metadata": {
            "source": "Cardiac Imaging",
            "category": "chest_xray",
            "modality": "xray",
            "topic": "cardiac"
        }
    },
    {
        "text": "Pleural effusion appears as blunting of the costophrenic angle on upright chest X-ray, with a meniscus sign in larger effusions. Lateral decubitus views can help confirm free-flowing fluid.",
        "metadata": {
            "source": "Thoracic Imaging",
            "category": "chest_xray",
            "modality": "xray",
            "topic": "pleural_effusion"
        }
    },
    {
        "text": "Pulmonary edema shows bilateral perihilar infiltrates in a butterfly pattern with Kerley B lines, often associated with cardiomegaly in cases of cardiac origin.",
        "metadata": {
            "source": "Chest Radiology",
            "category": "chest_xray",
            "modality": "xray",
            "topic": "pulmonary_edema"
        }
    },
    {
        "text": "Atelectasis appears as increased opacity with volume loss, displacement of fissures, and compensatory hyperinflation of adjacent lung segments.",
        "metadata": {
            "source": "Pulmonary Imaging",
            "category": "chest_xray",
            "modality": "xray",
            "topic": "atelectasis"
        }
    },
    {
        "text": "Rib fractures may show cortical disruption, displacement, or associated subcutaneous emphysema. Healing fractures develop callus formation over time.",
        "metadata": {
            "source": "Musculoskeletal Radiology",
            "category": "chest_xray",
            "modality": "xray",
            "topic": "fracture"
        }
    },
    {
        "text": "Lung nodules smaller than 3cm should be characterized by size, density, margins, and location. Smooth margins suggest benign etiology while spiculated margins raise concern for malignancy.",
        "metadata": {
            "source": "Oncologic Imaging",
            "category": "chest_xray",
            "modality": "xray",
            "topic": "nodule"
        }
    },
    {
        "text": "COPD findings include hyperinflation with flattened diaphragms, increased retrosternal airspace, and attenuated vascular markings. Bullae may be present in advanced disease.",
        "metadata": {
            "source": "Chronic Disease Imaging",
            "category": "chest_xray",
            "modality": "xray",
            "topic": "copd"
        }
    }
]


def load_sample_knowledge():
    """Load sample radiology knowledge into vector store."""
    store = get_knowledge_store()
    
    print(f"Loading {len(RADIOLOGY_KNOWLEDGE)} knowledge documents...")
    
    for idx, doc in enumerate(RADIOLOGY_KNOWLEDGE, 1):
        doc_id = store.add_knowledge(
            text=doc["text"],
            metadata=doc["metadata"]
        )
        print(f"  {idx}. Added: {doc['metadata']['topic']} (ID: {doc_id[:8]}...)")
    
    total = store.count()
    print(f"\n✅ Knowledge base ready! Total documents: {total}")
    
    # Test search
    print("\n🔍 Testing search...")
    results = store.search("patient with cough", limit=2, score_threshold=0.0)
    print(f"Found {len(results)} relevant documents:")
    for r in results:
        print(f"  - {r['topic']} (score: {r['score']:.2f})")


if __name__ == "__main__":
    load_sample_knowledge()