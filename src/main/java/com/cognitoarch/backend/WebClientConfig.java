package com.cognitoarch.backend;


import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.client.WebClient;

@Configuration
public class WebClientConfig {

    @Value("${PYTHON_BASE_URL:http://python:5000}")
    private String pythonBaseUrl;

    @Bean
    public WebClient pythonClient(WebClient.Builder builder) {
        return builder.baseUrl(pythonBaseUrl).build();
    }
}
