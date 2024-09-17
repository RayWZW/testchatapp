package com.example.chatapp;

import java.util.HashMap;
import java.util.Map;

public class Auth {
    private static Map<String, String> users = new HashMap<>();

    static {
        // Load users from a persistent storage in a real application
        users.put("testUser", "testPassword"); // example user
    }

    public static boolean authenticate(String username, String password) {
        return users.containsKey(username) && users.get(username).equals(password);
    }

    public static boolean register(String username, String password) {
        if (users.containsKey(username)) {
            return false; // User already exists
        }
        if (username.length() >= 6 && password.length() >= 6) {
            users.put(username, password);
            return true;
        }
        return false; // Validation failed
    }
}
