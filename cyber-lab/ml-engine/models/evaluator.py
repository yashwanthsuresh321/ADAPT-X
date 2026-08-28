import logging
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score

logger = logging.getLogger("models.evaluator")

def evaluate_model(model, X_test, y_test, feature_schema):
    """
    Evaluates the model and logs metrics, feature importances, and confusion matrix.
    """
    if X_test is None or len(X_test) == 0:
        logger.warning("Test set is empty. Skipping evaluation.")
        return
        
    y_pred = model.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    
    # We use macro average in case of multi-class or binary with arbitrary string labels
    # If binary and we want 'suspicious' as positive class, we can set pos_label
    is_binary = len(set(y_test)) == 2
    pos_label = 'suspicious' if 'suspicious' in set(y_test) else None
    
    if is_binary and pos_label:
        prec = precision_score(y_test, y_pred, pos_label=pos_label, zero_division=0)
        rec = recall_score(y_test, y_pred, pos_label=pos_label, zero_division=0)
        f1 = f1_score(y_test, y_pred, pos_label=pos_label, zero_division=0)
        
        try:
            y_prob = model.predict_proba(X_test)[:, model.classes_.tolist().index(pos_label)]
            roc = roc_auc_score(y_test, y_prob)
        except:
            roc = "N/A"
    else:
        prec = precision_score(y_test, y_pred, average='macro', zero_division=0)
        rec = recall_score(y_test, y_pred, average='macro', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='macro', zero_division=0)
        roc = "N/A"
        
    cm = confusion_matrix(y_test, y_pred, labels=model.classes_)
    
    logger.info(f"Accuracy: {acc:.4f}")
    logger.info(f"Precision: {prec:.4f}")
    logger.info(f"Recall: {rec:.4f}")
    logger.info(f"F1 Score: {f1:.4f}")
    logger.info(f"ROC-AUC: {roc}")
    logger.info(f"Confusion Matrix (labels={model.classes_}):\n{cm}")
    
    # Feature Importances
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
        feat_imp = sorted(zip(feature_schema, importances), key=lambda x: x[1], reverse=True)
        logger.info("Top Features:")
        for f, imp in feat_imp[:5]:
            logger.info(f"  - {f}: {imp:.4f}")
