package com.xpochecker.hooktraffic;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

import com.alibaba.fastjson.JSON;

public class SocketClientTest {
    public static final String HOST = "127.0.0.1";

    public static final int PORT = 50001;


    public static void main(String[] args) {

    }

    public static String getSocketServerMsg(String host, int port, String message) throws Exception {
        Socket socket = new Socket(host, port);

        OutputStream outputStream = socket.getOutputStream();
        PrintWriter printWriter = new PrintWriter(outputStream);
        printWriter.write(message);
        printWriter.flush();

        socket.shutdownOutput();

        InputStream inputStream = socket.getInputStream();

        byte[] bytes = new byte[1024];
        int len;
        StringBuilder sb = new StringBuilder();
        while ((len = inputStream.read(bytes)) != -1) {
            sb.append(new String(bytes, 0, len, StandardCharsets.UTF_8));
        }
        inputStream.close();
        outputStream.close();
        socket.close();

        return sb.toString();
    }
}
