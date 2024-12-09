provider "aws" {
  region = var.AWS_REGION
}

data "aws_iam_role" "ecs_task_execution_role" {
  name = "ecs_task_execution_role" 
}

resource "aws_ecs_task_definition" "c14_ellie_etl_task_definition" {
  family                   = "c14_ellie_etl_pipeline_task2"
  container_definitions    = jsonencode([
    {
      name        = "c14_ellie_etl_container"
      image       = var.ECR_IMAGE  
      memory      = 512
      cpu         = 256
      essential   = true
      environment = [
        {
          name  = "ACCESS_KEY_ID"
          value = var.ACCESS_KEY_ID 
        },
        {
          name  = "SECRET_ACCESS_KEY"
          value = var.SECRET_ACCESS_KEY
        },
        {
          name  = "BUCKET"
          value = var.S3_BUCKET
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-create-group"  = "true"
          "awslogs-group"         = "/ecs/c14_ellie_etl_pipeline2"
          "awslogs-region"        = var.AWS_REGION
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  memory                   = "512"
  cpu                      = "256"
  execution_role_arn       = data.aws_iam_role.ecs_task_execution_role.arn
}
