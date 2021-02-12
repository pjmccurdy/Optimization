import java.io.*;
import java.net.*;

//establish a server
//send data to client (indoor temp, outdoor temp, solar radiation, pricing);
//receive optimized energy usage




public class OptimizationServer{
    public static void main(String args[]) throws Exception {

        // Data from EP, weather file, and pricing federate

        double indoorTemp = 20.0;
	double outdoorTemp = 15.0; // eventually will be an array/matrix fo rnext four hours
	double solarRadiation = 0.0; // eventually will be an array/matrix for next four hours
	double pricing = 0.20; // eventually will be an array/matrix for next four hours


        // Convert data into string to be able to be sent via TCP/IP
	String data = String.valueOf(indoorTemp);
        data = data + "," + String.valueOf(outdoorTemp);

        // TCP/IP 

        String fromClient;
	String toClient;

	ServerSocket Server = new ServerSocket (5000); //ensure port number is the same in the server and client code
	System.out.println ("TCPServer Waiting for client on port 5000");

	boolean run = true;
	while(run) {
	    Socket connected = Server.accept();
            System.out.println( "The client"+" "+ connected.getInetAddress() +":"+connected.getPort()+" is connected"); //confirming connection

            BufferedReader inFromClient = new BufferedReader(new InputStreamReader (connected.getInputStream()));
            PrintWriter out = new PrintWriter(connected.getOutputStream(),true);

            toClient = data;
            System.out.println("send Indoor Temp as:" + indoorTemp);
	    System.out.println("send Outdoor Temp as:" + outdoorTemp);
            out.println(toClient);

            fromClient = inFromClient.readLine();
            System.out.println("Optimized Energy Usage for next hour:" + fromClient);

            connected.close();
	    run = false;
            System.out.println("socket closed");


//            if ( fromClient.equals("q") || fromClient.equals("Q") ) {
//                toClient = "eyB";
//                System.out.println("send eyB");
//                out.println(toClient);
//                connected.close();
//                run=false;
//                System.out.println("socket closed");
//            }
//            else {
//                System.out.println( "RECIEVED:" + fromClient );
//            }
        }
        System.exit(0);
    }
}
