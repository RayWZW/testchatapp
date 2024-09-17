package com.example.chatapp;

import java.text.SimpleDateFormat;
import java.util.Date;

public class Timestamps {
    private static final SimpleDateFormat formatter = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");

    public static String getCurrentTimestamp() {
        return formatter.format(new Date());
    }
}
