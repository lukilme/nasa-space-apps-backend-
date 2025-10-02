package com.cognitoarch.backend.controller;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.http.MediaType;
import org.springframework.http.codec.ServerSentEvent;
import org.springframework.web.reactive.function.client.WebClient;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import reactor.core.publisher.Flux;
import org.springframework.web.bind.annotation.CrossOrigin;

import java.util.Map;
import java.util.Objects;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@RestController
@CrossOrigin(origins = "http://127.0.0.1:5000")
public class TestController {

    private final WebClient pythonClient;
    private static final Logger logger = LoggerFactory.getLogger(TestController.class);

    public TestController(WebClient pythonClient) {
        this.pythonClient = pythonClient;
    }

    @PostMapping(value = "/ask", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<ServerSentEvent<Map<String, Object>>> ask(@RequestBody Map<String, String> body) {
        String prompt = body.get("question");
        logger.info("Received request for prompt: '{}'", prompt);

        Flux<Map<String, Object>> pythonFlux = pythonClient.post()
                .uri("/ask")
                .header("Content-Type", "application/json")
                .bodyValue(Map.of("question", prompt))
                .retrieve()
                .bodyToFlux(String.class)
                .map(this::parseSSEEvent)
                .filter(Objects::nonNull)
                .doOnNext(data -> logger.debug("Processed event: {}", data))
                .doOnError(error -> logger.error("Error calling Python API: {}", error.getMessage()))
                .doOnComplete(() -> logger.info("Stream completed successfully for prompt: '{}'", prompt));

        return pythonFlux.map(event -> ServerSentEvent.<Map<String, Object>>builder()
                .data(event)
                .build());
    }

    private Map<String, Object> parseSSEEvent(String rawData) {
        try {
            String jsonStr = rawData.startsWith("data: ") ? rawData.substring(6) : rawData;
            jsonStr = jsonStr.trim();

            if (jsonStr.isEmpty()) {
                return null;
            }

            ObjectMapper mapper = new ObjectMapper();
            Map<String, Object> event = mapper.readValue(jsonStr, new TypeReference<Map<String, Object>>() {
            });

            logger.debug("Parsed SSE event: {}", event);
            return event;

        } catch (Exception e) {
            logger.error("Error parsing SSE event: {}, error: {}", rawData, e.getMessage());

            return Map.of(
                    "type", "token",
                    "text", "Erro ao processar resposta: " + e.getMessage());
        }
    }
}
