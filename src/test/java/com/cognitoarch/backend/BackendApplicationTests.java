package com.cognitoarch.backend;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class BackendApplicationTests {

	@Test
	void contextLoads() {
		try {
			Class.forName("org.postgresql.Driver");
			System.out.println("Driver encontrado!");
		} catch (ClassNotFoundException e) {
			System.out.println("Driver não encontrado.");
		}
	}

}
