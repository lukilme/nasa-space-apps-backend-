package com.cognitoarch.backend;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfig implements WebMvcConfigurer {
    @SuppressWarnings("null")
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry
          .addMapping("/**")  // aplica a todas rotas
          .allowedOrigins("http://127.0.0.1:5000")  // ou "*" para permitir qualquer origem
          .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
          .allowedHeaders("*")
          .allowCredentials(true);  // se você quiser enviar cookies/credenciais
    }
}
