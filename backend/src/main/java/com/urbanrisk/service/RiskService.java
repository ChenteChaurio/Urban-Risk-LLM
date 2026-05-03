package com.urbanrisk.service;

import com.urbanrisk.model.QueryLog;
import com.urbanrisk.model.QueryLogRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.util.Map;

@Service
public class RiskService {

    private final WebClient webClient;
    private final QueryLogRepository logRepository;

    public RiskService(@Value("${ml.service.url}") String mlUrl,
            QueryLogRepository logRepository) {
        this.webClient = WebClient.builder().baseUrl(mlUrl).build();
        this.logRepository = logRepository;
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> predict(Map<String, Object> body, String tenantId) {
        Map<String, Object> response = webClient.post()
                .uri("/predict")
                .header("x-tenant-id", tenantId)
                .bodyValue(body)
                .retrieve()
                .bodyToMono(Map.class)
                .map(m -> (Map<String, Object>) m)
                .block();

        if (response != null) {
            logRepository.save(new QueryLog(
                    tenantId,
                    String.valueOf(body.getOrDefault("intersection_name", "unknown")),
                    "predict",
                    String.valueOf(response.getOrDefault("model_used", "?")),
                    String.valueOf(response.getOrDefault("risk_label", "?")),
                    toDouble(response.get("latency_ms"))));
        }
        return response;
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> explain(Map<String, Object> body, String tenantId) {
        Map<String, Object> response = webClient.post()
                .uri("/explain")
                .header("x-tenant-id", tenantId)
                .bodyValue(body)
                .retrieve()
                .bodyToMono(Map.class)
                .map(m -> (Map<String, Object>) m)
                .block();

        if (response != null) {
            logRepository.save(new QueryLog(
                    tenantId,
                    String.valueOf(body.getOrDefault("intersection_name", "unknown")),
                    "explain",
                    "rag",
                    String.valueOf(body.getOrDefault("risk_label", "?")),
                    toDouble(response.get("latency_ms"))));
        }
        return response;
    }

    public Map<?, ?> getMetrics() {
        return webClient.get()
                .uri("/metrics")
                .retrieve()
                .bodyToMono(Map.class)
                .block();
    }

    public Map<?, ?> mlHealth() {
        return webClient.get()
                .uri("/health")
                .retrieve()
                .bodyToMono(Map.class)
                .block();
    }

    private Double toDouble(Object val) {
        if (val == null)
            return null;
        try {
            return Double.parseDouble(val.toString());
        } catch (Exception e) {
            return null;
        }
    }
}
