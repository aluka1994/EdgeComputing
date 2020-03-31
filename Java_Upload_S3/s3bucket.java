/** author: alukaraj **/
package com.amazonaws.samples;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.Writer;
import java.util.ArrayList;
import java.util.UUID;
import com.amazonaws.samples.XferMgrUpload;

import com.amazonaws.AmazonClientException;
import com.amazonaws.AmazonServiceException;
import com.amazonaws.auth.AWSCredentials;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.profile.ProfileCredentialsProvider;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.model.Bucket;
import com.amazonaws.services.s3.model.ObjectListing;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import com.amazonaws.services.s3.transfer.TransferManager;
import com.amazonaws.services.s3.transfer.TransferManagerBuilder;
import com.amazonaws.services.sqs.AmazonSQS;
import com.amazonaws.services.sqs.AmazonSQSClientBuilder;
import com.amazonaws.services.sqs.model.*;

public class s3bucket {

	public static void main(String[] args) throws IOException {
		// TODO Auto-generated method stub
		AWSCredentials credentials = null;
        try {
            credentials = new ProfileCredentialsProvider("default").getCredentials();
        } catch (Exception e) {
            throw new AmazonClientException(
                    "Cannot load the credentials from the credential profiles file. " +
                    "Please make sure that your credentials file is at the correct " +
                    "location (/Users/alukaraju/.aws/credentials), and is in valid format.",
                    e);
        }
        
        System.out.println("Given AWS accessID : " + credentials.getAWSAccessKeyId());
        
        AmazonS3 s3 = AmazonS3ClientBuilder.standard()
                .withCredentials(new AWSStaticCredentialsProvider(credentials))
                .withRegion("us-east-1")
                .build();
        // checking if there are already any existing buckets.
        
        System.out.println("Total Buckets : " + s3.listBuckets().size());
        int bucketLength = s3.listBuckets().size();
        
        
        if(bucketLength > 0) {
        	// printing all the existing buckets.
        	System.out.println("Listing all the S3 Buckets");
            for (Bucket bucket : s3.listBuckets()) {
            	String tempBucket = bucket.getName();
            	System.out.println("Deleting S3 Bucket : " + bucket.getName());
                
                System.out.println("successfully deleted the s3 bucket : " + tempBucket);
                
                 
                    /* Get list of objects in a given bucket */
                    ObjectListing objects = s3.listObjects(bucket.getName());
                     
                    /* Recursively delete all the objects inside given bucket */
                    if(objects != null && objects.getObjectSummaries() != null) {               
                        while (true) {                  
                            for(S3ObjectSummary summary : objects.getObjectSummaries()) {
                                s3.deleteObject(bucket.getName(), summary.getKey());
                            }
                             
                            if (objects.isTruncated()) {
                                objects = s3.listNextBatchOfObjects(objects);
                            } else {
                                break;
                            }                   
                        }
                    }
                    s3.deleteBucket(bucket.getName());
            }
            
            
        }
        else {
        	System.out.println("There are No s3 buckets");
        }
        
        
        String bucketName = "my-first-s3-bucket-" + UUID.randomUUID();
       

        System.out.println("===========================================");
        System.out.println("Getting Started with Amazon S3");
        System.out.println("===========================================\n");
            
        try {
            //creating s3 bucket code.
            System.out.println("Creating bucket " + bucketName + "\n");
            s3.createBucket(bucketName);
                
            // printing all the existing buckets to check whether it has created or not.
            System.out.println("Listing buckets");
            for (Bucket bucket : s3.listBuckets()) {
            	System.out.println(" - " + bucket.getName());
            	
            }
            System.out.println();
            
            //File file1 = new File("/Users/alukaraju/ASU_studies/cloud/aws-java-sample/README.md");
            File file3 = new File("/Users/alukaraju/ASU_studies/cloud/aws-java-sample/README.md");
            File file = new File("/Users/alukaraju/Downloads/ty/jt1.mkv");
            File file2 = new File("/Users/alukaraju/Downloads/ty/jt2.mkv");
            /* Set Object Key */
            //String objectKey = file.getName();
             
            /* Send Put Object Request */
            //PutObjectResult result = s3.putObject(bucketName, objectKey, file);
            
            //System.out.println("Uploading a new object to S3 from a file\n " + (.getVersionId()));
            //s3.putObject(new PutObjectRequest(bucketName, createSampleFile().getName(),createSampleFile()));
            
            //System.out.println("successfully uploaded the");
            ArrayList<File> files_to_copy = new ArrayList<File>();
           
            files_to_copy.add(file);
            //files_to_copy.add(file1);
            files_to_copy.add(file3);
            files_to_copy.add(file2);
            
            int flength = files_to_copy.size();
            System.out.println("No of Files to be uploaded: " + Integer.toString(flength));
            
            AmazonSQS sqs = AmazonSQSClientBuilder.standard()
                    .withCredentials(new AWSStaticCredentialsProvider(credentials))
                    .withRegion("us-east-1")
                    .build();
            
			//CreateQueueRequest temp = new CreateQueueRequest().withName("cloudQueue");
            final String myQueueUrl = sqs.createQueue("CloudQueue").getQueueUrl();
            
            for(int i=0;i<flength;i++) {
            	AmazonS3 s4 = AmazonS3ClientBuilder.standard()
                    .withCredentials(new AWSStaticCredentialsProvider(credentials))
                    .withRegion("us-east-1")
                    .build();
            
            	
            	TransferManager xfer_mgr = TransferManagerBuilder.standard().withS3Client(s4).build();
            	XferMgrUpload.uploadFile(files_to_copy.get(i),bucketName,files_to_copy.get(i).getName(),false,xfer_mgr);
            	sqs.sendMessage(new SendMessageRequest(myQueueUrl,
                        files_to_copy.get(i).getName()+ "*noResult"));
            	//xfer_mgr.shutdownNow();
            }
            
         
            //System.out.println("New Queue : " + Integer.toString(myQueueUrl.length()));
            // List all queues.
            System.out.println("Listing all queues in your account.\n");
            for (final String queueUrl : sqs.listQueues().getQueueUrls()) {
                System.out.println("  QueueUrl: " + queueUrl);
            }
            
            System.out.println("Creating a new SQS queue called MyQueue.\n"); 
            
            
        }
        catch (AmazonServiceException ase) {
            	
        }
        catch (AmazonClientException ace) {
            	
        }
        
	}
	
	
	 
	// temp data to createfile
	private static File createSampleFile() throws IOException {
        File file = File.createTempFile("aws-java-sdk-", ".txt");
        //file.deleteOnExit();
        Writer writer = new OutputStreamWriter(new FileOutputStream(file));
        writer.write("abcdefghijklmnopqrstuvwxyz\n");
        writer.write("01234567890112345678901234\n");
        writer.write("!@#$%^&*()-=[]{};':',.<>/?\n");
        writer.write("01234567890112345678901234\n");
        writer.write("abcdefghijklmnopqrstuvwxyz\n");
        writer.close();

        return file;
    }

}
