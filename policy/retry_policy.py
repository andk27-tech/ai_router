class RetryPolicy:
    def __init__(self, max_retry=2, score_threshold=0.7):
        self.max_retry = max_retry
        self.score_threshold = score_threshold

    def should_retry(self, node_result):
        """
        node_result:
        {
            "score": float,
            "retry_count": int
        }
        """

        if node_result["retry_count"] >= self.max_retry:
            return False

        if node_result["score"] >= self.score_threshold:
            return False

        return True
