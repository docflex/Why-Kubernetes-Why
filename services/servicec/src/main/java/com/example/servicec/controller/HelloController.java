package com.example.servicec.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {
    private final String instanceId = java.util.UUID.randomUUID().toString();
    @GetMapping("/hello")
    public String hello() {
        return "Hello from Service C - Instance ID: " + instanceId;
    }
}
