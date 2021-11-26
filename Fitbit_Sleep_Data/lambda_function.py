# Vindhya Nair 
# lambda_function.py
# 12/7/2020
import json
import fitbit
from datetime import datetime
import boto3

# Add client ID and secret to authorize
CLIENT_ID = ''
CLIENT_SECRET = ''
TABLE_NAME = 'Fitbit_Sleep_Data_Store'

# CODE TO FETCH SLEEP DATA OF THE USER
def lambda_handler(event, context):
	debug_msg = "Lambda Start;"
	status = 'success'
# If lambda1(Fitbit_Access_Refresh_Tokens) is invoking lambda2((Fitbit_Sleep_Data)) then replace the below line with params = event
	try:
		params = event["queryStringParameters"]
		token = params["token"]
		debug_msg += "Got Token"
		refresh_token = params["refresh_token"]
		debug_msg += "refresh_token"
		user_id = params["user_id"]
		debug_msg += "Got userid"
		user_name = params["user_name"]
		debug_msg += "Got username"
		fetch_date = params["fetch_date"]
		debug_msg += "Got Date"

		date_time = datetime.strptime(fetch_date,'%b %d %Y %H:%M:%S')
		debug_msg += "date_time"

		authd_client = fitbit.Fitbit(CLIENT_ID, CLIENT_SECRET, access_token=token, refresh_token=refresh_token)
		debug_msg += "authd_client"
		sleep_data = authd_client.sleep(date=date_time)
		debug_msg += "sleep_data"
		
		newItemDB(user_id,user_name,date_time,sleep_data)
		debug_msg += "newItemDB"

	except Exception as e:
		debug_msg += "Caught exception" + str(e)
		status = 'failure'

	returnData = {
		'status' : status,
		'debug_msg':debug_msg
	}

	return {
	'statusCode': 200,
	'body': json.dumps(returnData)	
	}

# Method to put the sleep data of the user into Dynamo DB table Store_Fitbit_Sleep_Data
def newItemDB(user_id,user_name,pstTime,sleep_data):
	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table(TABLE_NAME)
	response = table.put_item (
		TableName=TABLE_NAME,Item={"userid": user_id,"user_name":user_name,"date":str(pstTime),"sleep_data":sleep_data}

	)

# To debug in local uncomment below code
""" def main():
	cxt =None
	evt = { "queryStringParameters":{ "code": "" } }	
	lambda_handler(evt, cxt)


if __name__ == "__main__":
    main()
 """

