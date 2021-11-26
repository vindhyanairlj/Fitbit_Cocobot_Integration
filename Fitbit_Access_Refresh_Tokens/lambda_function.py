# Vindhya Nair
# lambda_function.py
# 11/11/2021
import json
import requests
import datetime
import boto3

# Add client ID and secret to authorize
CLIENT_ID = ''
REDIRECTURI = ''
#TABLE_NAME = 'Store_Fitbit_Access_Refresh_Tokens'
TABLE_NAME = 'Fitbit_Access_Refresh_Tokens_Store'
AUTHORIZATION_INFO = ''

# CODE TO AUTHORIZE THE USER.
def lambda_handler(event, context):
	debug_msg = "Lambda start;"
	status = 'failure'
	token = ''
	rToken = ''

	try:	
		params = event["queryStringParameters"]
		code = params["code"]
		user_id = params["user_id"]
		user_name = params["user_name"]
	
		url = 'https://api.fitbit.com/oauth2/token'
		load = {'code': code, 'grant_type': 'authorization_code', 'client_id': CLIENT_ID, 'redirect_uri': REDIRECTURI}
		headers = {'Authorization': AUTHORIZATION_INFO, 'Content-Type': 'application/x-www-form-urlencoded'}
		r = requests.post(url, params=load, headers=headers)

		debug_msg += " request posted;"
		response = r.json()
		print("Response",response)
		
		token = response['access_token']
		rToken = response['refresh_token']
		debug_msg += " got tokens;"
		
		pstTime = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7)))
		newItemDB(user_id,user_name,token,rToken,str(pstTime))
		debug_msg += " put item table;"
		
		# In order to call Lambda2 from Lamba1 uncomment below line and corresponding method. 
		# Just make sure the date is of the format "Oct 24 2021 11:31:00"
		# call_Lambda2(token,rToken,user_id,user_name,str(pstTime))

		# When we reach here everything worked fine.
		status = 'success'
	except Exception as e:
		debug_msg += "Caught exception" + str(e)
		status = 'failure'

	returnData = {
		'status' : status,
		'access_token':token,
		'refresh_token': rToken,
		'debug_message':debug_msg
	}

	return {
	'statusCode': 200,
	'body': json.dumps(returnData)	
	}

# Method to put the access token and refresh token into Dynamo DB table Store_Fitbit_Access_Refresh_Tokens
def newItemDB(user_id,user_name,token,rToken,pstTime):
	dynamodb = boto3.resource('dynamodb')
	table = dynamodb.Table(TABLE_NAME)
	response = table.put_item (
		TableName=TABLE_NAME,Item={"userid": user_id,"user_name":user_name,"access_token":token,"refresh_token":rToken,"pstTime":pstTime}

	)

# Uncomment below lines if you want lambda1(Fitbit_Access_Refresh_Tokens) to invoke lambda2(Fitbit_Sleep_Data)
""" def call_Lambda2(token,rToken,user_id,user_name,date):
	client=boto3.client('lambda')
	inputForInvoker = {"userid": user_id,"user_name":user_name,"access_token":token,"refresh_token":rToken,"fetch_date":date}
	client.invoke(FunctionName='',InvocationType='Event',Payload=json.dumps(inputForInvoker))
 """

# Uncomment below code if you want to debug locally. Use new value for variable code
""" def main():
	cxt =None
	evt = { "queryStringParameters":{ "code": "" } }	
	lambda_handler(evt, cxt)

if __name__ == "__main__":
    main() """
 

