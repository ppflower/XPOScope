package com.xpochecker.hooktraffic;


import com.alibaba.fastjson.JSON;

import org.apache.commons.lang3.StringEscapeUtils;

import java.io.BufferedWriter;
import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.io.OutputStreamWriter;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

import de.robv.android.xposed.IXposedHookLoadPackage;
import de.robv.android.xposed.XC_MethodHook;
import de.robv.android.xposed.XposedBridge;
import de.robv.android.xposed.XposedHelpers;
import de.robv.android.xposed.callbacks.XC_LoadPackage;

public class HookAliPay implements IXposedHookLoadPackage {
    public static final String HOST = "127.0.0.1";

    public static final int PORT = 9999;

    public static void sendMessage(String socketData) {
        if (socketData.length() == 0)
            return;

        String TAG = "AliPaySocket";
        try {
            XposedBridge.log(TAG + " socket send Data: " + socketData);
            String socketServerMsg = getSocketServerMsg(HOST, PORT, socketData);
            XposedBridge.log(TAG + " socket message: " + socketServerMsg);
            Thread.sleep(1000);
        } catch (Exception e) {
            XposedBridge.log(TAG + " AliPay Message fail to send");
        }

    }

    public static boolean getJSONType(String str) {
        boolean res = false;
        try {
            Object obj = JSON.parse(str);
            res = true;
        } catch (Exception ignored) {
        }
        return res;
    }

    public static String getSocketServerMsg(String host, int port, String message) throws Exception {
        Socket socket = new Socket(host, port);
        BufferedWriter out = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream()));
        out.write(message);
        out.flush();
        out.write("Bye");
        out.flush();
        return "Connect Success";
    }

    public boolean isGzipTraffic(String contentEncoding, String contentType) {
        return "gzip".equals(contentEncoding) && contentType != null && (contentType.contains("json") || contentType.contains("html"));
    }

    @Override
    public void handleLoadPackage(XC_LoadPackage.LoadPackageParam loadPackageParam) throws Throwable {
        if (!loadPackageParam.packageName.equalsIgnoreCase("com.eg.android.AlipayGphone"))
            return;

        final Class<?> httpManagerClass = XposedHelpers.findClass("com.alipay.mobile.common.transport.http.HttpManager", loadPackageParam.classLoader);
        final Class<?> httpRequestClass = XposedHelpers.findClass("com.alipay.mobile.common.transport.Request", loadPackageParam.classLoader);

        XposedHelpers.findAndHookMethod("com.alipay.mobile.common.transport.http.inner.CoreHttpManager", loadPackageParam.classLoader, "execute", httpManagerClass, httpRequestClass, new XC_MethodHook() {
            @Override
            protected void afterHookedMethod(MethodHookParam param) throws Throwable {
                super.afterHookedMethod(param);
                String H5Tag = "AliReNetH5";
                final Class<?> futureClass = XposedHelpers.findClass("java.util.concurrent.Future", loadPackageParam.classLoader);
                Method futureGet = futureClass.getDeclaredMethod("get");
                futureGet.setAccessible(true);
                // Future<Response> ResponseObject提取 HttpUrlResponse extends Response && H5HttpUrlResponse extends HttpUrlResponse
                Object responseObject = futureGet.invoke(param.getResult());
                String managerName = param.args[0].getClass().getName();
                String responseName = responseObject.getClass().getName();

//                XposedBridge.log(HttpTag + ": ManagerName:" + managerName);
//                XposedBridge.log(HttpTag + ": ResponseName" + responseName);

                managerName = managerName.split("\\.")[managerName.split("\\.").length - 1];
                responseName = responseName.split("\\.")[responseName.split("\\.").length - 1];

                final Class<?> httpUrlResponseClass = XposedHelpers.findClass("com.alipay.mobile.common.transport.http.HttpUrlResponse", loadPackageParam.classLoader);
                final Class<?> httpHeaderClass = XposedHelpers.findClass("com.alipay.mobile.common.transport.http.HttpUrlHeader", loadPackageParam.classLoader);

                /*通过提取ResponseObject中的HttpUrlHeaders*/
                Field httpHeaderField = httpUrlResponseClass.getDeclaredField("f");
                httpHeaderField.setAccessible(true);
                Object httpHeaderFieldInstance = httpHeaderField.get(responseObject);

                /*利用HttpUrlHeaders中的getHeaders函数序列化Headers 为Map<String,String>*/
                Map<String, String> headerMap = (Map<String, String>) httpHeaderClass.getDeclaredMethod("getHeaders").invoke(httpHeaderFieldInstance);
                String contentType = headerMap.get("content-type");
                String contentEncoding = headerMap.get("content-encoding");

//                XposedBridge.log(H5Tag + ": ContentType:" + contentType);
//                XposedBridge.log(H5Tag + ": ContentEncoding:" + contentEncoding);

                /*contentType 放在前面*/
                if (contentType != null && !contentType.contains("image")) {
                    if (managerName.equals("HttpManager")) {
                        String requestClassName = param.args[1].getClass().getName();

//                        XposedBridge.log(HttpTag + ": Request: " + param.args[1]);
//                        XposedBridge.log(HttpTag + ": RequestClassName: " + requestClassName);
//                        XposedBridge.log(HttpTag + ": FromManager: " + managerName + " ReturnResponse: " + responseName);
//                        XposedBridge.log(HttpTag + ": Headers: " + headerMap);

                    } else if (managerName.equals("H5NetworkManager")) {
                        String requestClassName = param.args[1].getClass().getName();

                        String paramStrAll = param.args[1].toString();
                        String[] paramStrs = paramStrAll.split(",");
                        String Url = null;
                        for (String paramStr : paramStrs) {
                            String prefix = "Url :";
                            if (paramStr.startsWith("Url :")) {
                                Url = paramStr.substring(prefix.length()).trim();
                            }
                        }

//                        XposedBridge.log(H5Tag + ": URL:" + Url);

                        final Class<?> h5ResClass = XposedHelpers.findClass("com.alipay.mobile.common.transport.h5.H5HttpUrlResponse", loadPackageParam.classLoader);
                        final Class<?> h5UtilsClass = XposedHelpers.findClass("com.alipay.mobile.nebula.util.H5Utils", loadPackageParam.classLoader);


                        java.io.InputStream responseInputStream = (java.io.InputStream) h5ResClass.getDeclaredMethod("getInputStream").invoke(responseObject);

                        final Class<?> h5InputStreamWraperClass = XposedHelpers.findClass("com.alipay.mobile.common.transport.h5.NetworkInputStreamWrapper", loadPackageParam.classLoader);

                        /*睡眠读取bytes*/
                        Thread.sleep(200);

                        byte[] bytesResponse = (byte[]) h5UtilsClass.getDeclaredMethod("readBytes", java.io.InputStream.class).invoke(null, responseInputStream);

                        /*
                         * 由于前期将InputStream流中内容读取，需要将流进行恢复，否则会导致报错，当然网上有一种inputStream.reset()方法可以后期试一试
                         * 构造新的流
                         * */
                        final Class<?> h5tcClass = XposedHelpers.findClass("com.alipay.mobile.common.transport.context.TransportContext", loadPackageParam.classLoader);
                        final Class<?> h5HttpWorkerClass = XposedHelpers.findClass("com.alipay.mobile.common.transport.http.HttpWorker", loadPackageParam.classLoader);
                        Field tc = h5InputStreamWraperClass.getDeclaredField("mTransportContext");
                        tc.setAccessible(true);
                        Field hm = h5InputStreamWraperClass.getDeclaredField("b");
                        hm.setAccessible(true);
                        Field hw = h5InputStreamWraperClass.getDeclaredField("d");
                        hw.setAccessible(true);
                        Field resInputStreamField = h5ResClass.getDeclaredField("a");
                        resInputStreamField.setAccessible(true);
                        java.io.InputStream newInputStream = (java.io.InputStream) h5InputStreamWraperClass.getConstructor(InputStream.class, h5tcClass, httpManagerClass, h5HttpWorkerClass).newInstance(new ByteArrayInputStream(bytesResponse), tc.get(responseInputStream), hm.get(responseInputStream), hw.get(responseInputStream));
                        resInputStreamField.set(responseObject, newInputStream);


                        byte[] gzip_bytesResponse = new byte[]{};
                        if (isGzipTraffic(contentEncoding, contentType)) {
                            final Class<?> gzipClass = XposedHelpers.findClass("java.util.zip.GZIPInputStream", loadPackageParam.classLoader);
                            java.io.InputStream tmpInputStream = (java.io.InputStream) gzipClass.getConstructor(java.io.InputStream.class).newInstance(new ByteArrayInputStream(bytesResponse));
                            gzip_bytesResponse = (byte[]) h5UtilsClass.getDeclaredMethod("readBytes", java.io.InputStream.class).invoke(null, tmpInputStream);
                            tmpInputStream.close();
                        }

                        String resString;
                        if (isGzipTraffic(contentEncoding, contentType)) {
                            resString = new String(gzip_bytesResponse, StandardCharsets.UTF_8);
                        } else {
                            resString = new String(bytesResponse, StandardCharsets.UTF_8);
                        }

                        XposedBridge.log(H5Tag + ": bytesResponseLength:" + bytesResponse.length);
                        String sendData = StringEscapeUtils.unescapeJava(resString);
                        XposedBridge.log(H5Tag + ": ResData:" + sendData);
                        sendData = sendData.trim();
                        if (sendData.length() > 0) {
                            Map<String, String> paramMap = new HashMap<>();

                            paramMap.put("opt_type", "1");
                            paramMap.put("url", Url);
                            if (sendData.length() % 1024 == 0) {
                                byte[] bytes = sendData.getBytes();
                                byte[] newBytes = new byte[bytes.length + 1];
                                System.arraycopy(bytes, 0, newBytes, 0, bytes.length);
                                sendData = new String(newBytes);
                            }
                            paramMap.put("data", sendData);

                            String socketData = JSON.toJSONString(paramMap);

                            if (getJSONType(socketData)) {
                                byte[] temp = socketData.getBytes(StandardCharsets.UTF_8);
                                socketData = new String(temp, StandardCharsets.UTF_8);
                                sendMessage(socketData);
                                XposedBridge.log(H5Tag + "String is Json");
                            } else {
                                XposedBridge.log(H5Tag + "String is not Json");
                            }
                        }
                    }
                }
            }
        });

    }
}
