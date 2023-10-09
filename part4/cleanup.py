# coding: UTF-8
import boto3


def get_aws_account_id(session):
    """
    AWSのアカウントIDを返します。
    :param なし
    :return: AWSのアカウントを示す12桁のID
    """
    sts = session.client('sts')
    id_info = sts.get_caller_identity()
    return id_info['Account']


def delete_stack(cloudformation, stackname):

    try:
        cloudformation.delete_stack(
            StackName=stackname
        )
        waiter = cloudformation.get_waiter('stack_delete_complete')
        waiter.wait(StackName=stackname,
                    WaiterConfig={
                        'Delay': 5,
                        'MaxAttempts': 3
                    })
    except Exception as e:
        print(e)


# entry point
if __name__ == '__main__':

    print(f"boto3 version: {boto3.__version__}")
    print("session start")
    session = boto3.Session(profile_name="cicd_handson",
                            region_name='ap-northeast-1')

    aws_account_id = get_aws_account_id(session)

    try:
        hanson_bucket_name = f'cicdhandson-bucket-{aws_account_id}'

        s3 = session.resource('s3')
        bucket = s3.Bucket(hanson_bucket_name)

        s3_objects = list(bucket.objects.all())
        for s3_object in s3_objects:
            s3_object.delete()

        s3_object_versions = list(bucket.object_versions.all())
        for s3_object_version in s3_object_versions:
            s3_object_version.delete()

        s3_objects = list(bucket.objects.all())

        if not s3_objects:
            print("delete s3 objects OK")
        else:
            print("delete s3 objects NG")
    except Exception as e:
        print(e)

    try:
        sam_build_bucket_name = f'sam-build-bucket-{aws_account_id}'

        s3 = session.resource('s3')
        bucket = s3.Bucket(sam_build_bucket_name)

        s3_objects = list(bucket.objects.all())
        for s3_object in s3_objects:
            s3_object.delete()

        s3_object_versions = list(bucket.object_versions.all())
        for s3_object_version in s3_object_versions:
            s3_object_version.delete()

        s3_objects = list(bucket.objects.all())

        if not s3_objects:
            print("delete s3 objects OK")
        else:
            print("delete s3 objects NG")
    except Exception as e:
        print(e)

    try:
        ecr = session.client('ecr')
        ecr_images = ecr.list_images(
            repositoryName="cicdhandson"
        )

        for imageId in ecr_images.get('imageIds'):
            ecr.batch_delete_image(
                repositoryName="cicdhandson",
                imageIds=imageId
            )

        ecr_images = ecr.list_images(
            repositoryName="cicdhandson"
        )
    except Exception as e:
        print(e)

    cloudformation = session.client('cloudformation')

    print("delete stacks")
    stack_names = [
        "infra-part4",
        "codecommit",
        "lambda",
        "my-date-time-app",
        "cicdhandson-user"
    ]

    for stack_name in stack_names:
        delete_stack(cloudformation=cloudformation, stackname=stack_name)

    cloudwatch = session.client('logs')

    try:
        cloudwatch.delete_log_group(
            logGroupName='/aws/codebuild/cicdhandson'
        )
    except Exception as e:
        print(e)

    try:
        cloudwatch.delete_log_group(
            logGroupName='/aws/lambda/cicdhandsonFunc'
        )
    except Exception as e:
        print(e)

    try:
        cloudwatch.delete_log_group(
            logGroupName='/aws/lambda/CodeDeployHook_beforeAllowTraffic'
        )
    except Exception as e:
        print(e)

    try:
        cloudwatch.delete_log_group(
            logGroupName='/aws/lambda/CodeDeployHook_afterAllowTraffic'
        )
    except Exception as e:
        print(e)

    try:
        log_groups = cloudwatch.describe_log_groups(
            logGroupNamePrefix='/aws/lambda/my-date-time-app-myDateTimeFunction'
        )
        for log_group in log_groups.get('logGroups'):
            cloudwatch.delete_log_group(
                logGroupName=log_group.get('logGroupName')
            )
    except Exception as e:
        print(e)

    print("session end")
