import java.io.*;
import java.net.*;

public class Optimization{
    public static void main(String args[]) throws Exception {
        String fromClient;
	String toClient;

	ServerSocket Server = new ServerSocket (5000);
	System.out.println ("TCPServer Waiting for client on port 5000");

	boolean run = true;
	while(run) {
	    Socket connected = Server.accept();
            System.out.println( "THE CLIENT"+" "+ connected.getInetAddress() +":"+connected.getPort()+" IS CONNECTED");

            BufferedReader inFromClient = new BufferedReader(new InputStreamReader (connected.getInputStream()));

            while (run) {
                fromClient = inFromClient.readLine();

                if ( fromClient.equals("q") || fromClient.equals("Q") ) {
                    connected.close();
                    break;
                }
                else {
                    System.out.println( "RECIEVED:" + fromClient );
                } 
            }
        }
    }
}
