"""
AWS Systems Engineer Role Context Module
Ensures all questions are focused on AWS Systems Engineer role
"""
from typing import Dict, List, Any


class AWSContext:
    """AWS Systems Engineer role context and prompts"""
    
    # AWS Systems Engineer Role Description
    ROLE_DESCRIPTION = """
    AWS Systems Engineers are responsible for:
    - Designing, deploying, and maintaining AWS infrastructure
    - Troubleshooting and optimizing AWS services and systems
    - Automating AWS operations and deployments
    - Monitoring and ensuring reliability of AWS-based systems
    - Implementing security best practices in AWS environments
    - Managing Linux systems running on AWS (EC2, ECS, EKS, Lambda)
    - Configuring and troubleshooting AWS networking (VPC, CloudFront, ALB, Route 53)
    - Implementing operational excellence using AWS services (CloudWatch, Systems Manager, etc.)
    """
    
    # Topic to AWS Service Mapping
    TOPIC_AWS_MAPPING = {
        "linux": {
            "services": ["EC2", "ECS", "EKS", "Lambda", "CloudWatch", "Systems Manager"],
            "context": "Focus on Linux systems running on AWS services like EC2, ECS, EKS, and Lambda",
            "examples": [
                "Linux processes on EC2 instances",
                "Memory management in ECS containers",
                "Package management in AWS AMIs",
                "Boot process in EC2 instances",
                "Security hardening for AWS-hosted Linux systems"
            ]
        },
        "networking": {
            "services": ["VPC", "CloudFront", "ALB", "NLB", "Route 53", "API Gateway", "ACM"],
            "context": "Focus on AWS networking services and protocols",
            "examples": [
                "TLS/SSL in CloudFront and ALB",
                "Certificate management with ACM",
                "Load balancing with AWS services",
                "VPC networking and security groups",
                "Route 53 DNS and CDN with CloudFront"
            ]
        },
        "operational-excellence": {
            "services": ["CloudWatch", "CloudTrail", "Systems Manager", "Auto Scaling", "X-Ray", "Step Functions"],
            "context": "Focus on AWS operational excellence services",
            "examples": [
                "Performance optimization of AWS services",
                "Automation with Systems Manager and Lambda",
                "Incident management with CloudWatch and CloudTrail",
                "Scaling AWS infrastructure"
            ]
        },
        "scripting": {
            "services": ["boto3", "AWS CLI", "CloudFormation", "Terraform", "Lambda", "Step Functions"],
            "context": "Focus on AWS automation and scripting",
            "examples": [
                "AWS CLI and boto3 scripting",
                "Infrastructure as Code with CloudFormation",
                "Log parsing from CloudWatch Logs",
                "AWS service integration scripts"
            ]
        }
    }
    
    # Subtopic mappings
    SUBTOPIC_MAPPINGS = {
        "linux": {
            "processes": {
                "aws_context": "Process management on EC2 instances, ECS containers, or EKS pods",
                "services": ["EC2", "ECS", "EKS", "CloudWatch", "Systems Manager"]
            },
            "memory": {
                "aws_context": "Memory management in AWS instances and containers",
                "services": ["EC2", "ECS", "EKS", "CloudWatch"]
            },
            "disk": {
                "aws_context": "Disk space and file systems in AWS (EBS, EFS)",
                "services": ["EC2", "EBS", "EFS", "CloudWatch"]
            },
            "package-management": {
                "aws_context": "Package management in AWS AMIs and containers",
                "services": ["EC2", "ECS", "EKS", "Systems Manager"]
            },
            "boot-process": {
                "aws_context": "Linux boot process in EC2 instances",
                "services": ["EC2", "Systems Manager"]
            },
            "daemons": {
                "aws_context": "Daemons and services in AWS environments",
                "services": ["EC2", "ECS", "EKS", "Systems Manager"]
            },
            "load-average": {
                "aws_context": "Load average monitoring in AWS",
                "services": ["EC2", "CloudWatch", "Auto Scaling"]
            },
            "shells": {
                "aws_context": "Shell usage in AWS environments",
                "services": ["EC2", "Systems Manager"]
            },
            "security-hardening": {
                "aws_context": "Security hardening for AWS-hosted Linux systems",
                "services": ["EC2", "Systems Manager", "IAM", "Security Groups"]
            },
            "troubleshooting": {
                "aws_context": "Complex Linux troubleshooting in AWS environments",
                "services": ["EC2", "ECS", "EKS", "CloudWatch", "Systems Manager", "X-Ray"]
            }
        },
        "networking": {
            "tls": {
                "aws_context": "TLS/SSL in AWS services (CloudFront, ALB, API Gateway)",
                "services": ["CloudFront", "ALB", "API Gateway", "ACM"]
            },
            "certificate-validation": {
                "aws_context": "Certificate validation and ACM (AWS Certificate Manager)",
                "services": ["ACM", "CloudFront", "ALB", "API Gateway"]
            },
            "load-balancing": {
                "aws_context": "Load balancing with AWS services (ALB, NLB, CloudFront)",
                "services": ["ALB", "NLB", "CloudFront", "Route 53"]
            },
            "troubleshooting": {
                "aws_context": "Network troubleshooting in AWS environments",
                "services": ["VPC", "CloudWatch", "VPC Flow Logs", "X-Ray"]
            }
        },
        "operational-excellence": {
            "performance": {
                "aws_context": "Performance optimization of AWS services",
                "services": ["CloudWatch", "X-Ray", "Auto Scaling", "ECS", "EKS"]
            },
            "automation": {
                "aws_context": "Automation with AWS services",
                "services": ["Systems Manager", "Lambda", "Step Functions", "CloudFormation"]
            },
            "incidents": {
                "aws_context": "Incident management with AWS services",
                "services": ["CloudWatch", "CloudTrail", "X-Ray", "Systems Manager"]
            },
            "scale": {
                "aws_context": "Scaling AWS infrastructure",
                "services": ["Auto Scaling", "ECS", "EKS", "Lambda", "CloudWatch"]
            }
        },
        "scripting": {
            "log-parsing": {
                "aws_context": "Parsing logs from AWS services (CloudWatch Logs, S3)",
                "services": ["CloudWatch Logs", "S3", "boto3", "AWS CLI"]
            },
            "system-maintenance": {
                "aws_context": "Automating system maintenance tasks in AWS",
                "services": ["Systems Manager", "Lambda", "boto3", "AWS CLI"]
            },
            "monitoring": {
                "aws_context": "Implementing monitoring scripts for AWS",
                "services": ["CloudWatch", "boto3", "Lambda", "AWS CLI"]
            },
            "text-manipulation": {
                "aws_context": "Text manipulation for AWS reporting",
                "services": ["S3", "boto3", "AWS CLI", "Lambda"]
            },
            "user-management": {
                "aws_context": "User management scripts for AWS",
                "services": ["IAM", "boto3", "AWS CLI", "Lambda"]
            }
        }
    }
    
    def get_role_system_prompt(self) -> str:
        """Returns AWS Systems Engineer role system prompt"""
        return f"""You are an expert at creating interview questions for AWS Systems Engineer positions.

{AWSContext.ROLE_DESCRIPTION}

All questions must be relevant to AWS Systems Engineer role and exclude generic IT topics not related to AWS."""

    def get_aws_context_prompt(self, topic: str, subtopic: str) -> str:
        """Returns AWS-specific context for topic/subtopic"""
        topic_info = self.TOPIC_AWS_MAPPING.get(topic.lower(), {})
        subtopic_info = self.SUBTOPIC_MAPPINGS.get(topic.lower(), {}).get(subtopic.lower(), {})
        
        context_parts = []
        
        if topic_info:
            context_parts.append(f"**Topic:** {topic.capitalize()}")
            context_parts.append(f"**AWS Context:** {topic_info.get('context', '')}")
            context_parts.append(f"**Relevant AWS Services:** {', '.join(topic_info.get('services', []))}")
        
        if subtopic_info:
            context_parts.append(f"**Subtopic:** {subtopic.capitalize()}")
            context_parts.append(f"**AWS Context:** {subtopic_info.get('aws_context', '')}")
            if subtopic_info.get('services'):
                context_parts.append(f"**Relevant AWS Services:** {', '.join(subtopic_info.get('services', []))}")
        
        return "\n".join(context_parts)
    
    def frame_question_for_aws_role(self, base_prompt: str, topic: str, subtopic: str) -> str:
        """Wraps prompt with AWS context"""
        system_prompt = self.get_role_system_prompt()
        aws_context = self.get_aws_context_prompt(topic, subtopic)
        
        return f"""{system_prompt}

{aws_context}

{base_prompt}"""
    
    def get_topics_structure(self) -> List[Dict[str, Any]]:
        """Returns structured topic hierarchy"""
        return [
            {
                "name": "linux",
                "description": "Linux systems in AWS environments",
                "subtopics": [
                    {"name": "processes", "description": "Process management in AWS", "recommended_difficulty_progression": ["newbie", "intermediate", "pro"]},
                    {"name": "memory", "description": "Memory management in AWS", "recommended_difficulty_progression": ["newbie", "intermediate", "pro"]},
                    {"name": "disk", "description": "Disk space and file systems", "recommended_difficulty_progression": ["newbie", "intermediate", "pro"]},
                    {"name": "package-management", "description": "Package management", "recommended_difficulty_progression": ["newbie", "intermediate"]},
                    {"name": "boot-process", "description": "Linux boot process", "recommended_difficulty_progression": ["newbie", "intermediate"]},
                    {"name": "daemons", "description": "Daemons and services", "recommended_difficulty_progression": ["newbie", "intermediate"]},
                    {"name": "load-average", "description": "Load average monitoring", "recommended_difficulty_progression": ["newbie", "intermediate", "pro"]},
                    {"name": "shells", "description": "Shell usage", "recommended_difficulty_progression": ["newbie", "intermediate"]},
                    {"name": "security-hardening", "description": "Security hardening", "recommended_difficulty_progression": ["intermediate", "pro"]},
                    {"name": "troubleshooting", "description": "Complex troubleshooting", "recommended_difficulty_progression": ["intermediate", "pro"]}
                ]
            },
            {
                "name": "networking",
                "description": "Networking in AWS",
                "subtopics": [
                    {"name": "tls", "description": "TLS in AWS", "recommended_difficulty_progression": ["newbie", "intermediate", "pro"]},
                    {"name": "certificate-validation", "description": "Certificate validation", "recommended_difficulty_progression": ["newbie", "intermediate", "pro"]},
                    {"name": "load-balancing", "description": "Load balancing techniques", "recommended_difficulty_progression": ["newbie", "intermediate", "pro"]},
                    {"name": "troubleshooting", "description": "Network troubleshooting", "recommended_difficulty_progression": ["intermediate", "pro"]}
                ]
            },
            {
                "name": "operational-excellence",
                "description": "Operational Excellence, Automation & Process Improvement",
                "subtopics": [
                    {"name": "performance", "description": "Performance optimization", "recommended_difficulty_progression": ["newbie", "intermediate", "pro"]},
                    {"name": "automation", "description": "Automation strategies", "recommended_difficulty_progression": ["newbie", "intermediate", "pro"]},
                    {"name": "incidents", "description": "Incident management", "recommended_difficulty_progression": ["newbie", "intermediate", "pro"]},
                    {"name": "scale", "description": "Scaling considerations", "recommended_difficulty_progression": ["newbie", "intermediate", "pro"]}
                ]
            },
            {
                "name": "scripting",
                "description": "Scripting for AWS automation",
                "subtopics": [
                    {"name": "log-parsing", "description": "Log parsing scenarios", "recommended_difficulty_progression": ["newbie", "intermediate", "pro"]},
                    {"name": "system-maintenance", "description": "System maintenance automation", "recommended_difficulty_progression": ["newbie", "intermediate", "pro"]},
                    {"name": "monitoring", "description": "Monitoring scripts", "recommended_difficulty_progression": ["newbie", "intermediate", "pro"]},
                    {"name": "text-manipulation", "description": "Text manipulation", "recommended_difficulty_progression": ["newbie", "intermediate"]},
                    {"name": "user-management", "description": "User management scripts", "recommended_difficulty_progression": ["newbie", "intermediate", "pro"]}
                ]
            }
        ]
    
    def get_learning_plan(self) -> Dict[str, Any]:
        """Returns learning plan structure"""
        return {
            "phases": [
                {
                    "phase": 1,
                    "name": "Foundation (Newbie Level)",
                    "description": "Build foundational knowledge",
                    "weeks": "Week 1-3",
                    "topics": [
                        {"topic": "linux", "subtopics": ["processes", "memory", "disk", "package-management", "boot-process", "daemons", "load-average", "shells"], "difficulty": "newbie"},
                        {"topic": "networking", "subtopics": ["tls", "certificate-validation", "load-balancing"], "difficulty": "newbie"}
                    ]
                },
                {
                    "phase": 2,
                    "name": "Application (Intermediate Level)",
                    "description": "Apply knowledge to practical scenarios",
                    "weeks": "Week 4-7",
                    "topics": [
                        {"topic": "linux", "subtopics": ["security-hardening", "troubleshooting"], "difficulty": "intermediate"},
                        {"topic": "networking", "subtopics": ["troubleshooting"], "difficulty": "intermediate"},
                        {"topic": "operational-excellence", "subtopics": ["performance", "automation", "incidents", "scale"], "difficulty": ["newbie", "intermediate"]},
                        {"topic": "scripting", "subtopics": ["log-parsing", "system-maintenance", "monitoring", "text-manipulation", "user-management"], "difficulty": ["newbie", "intermediate"]}
                    ]
                },
                {
                    "phase": 3,
                    "name": "Integration & Practice",
                    "description": "Cross-topic practice and real-world scenarios",
                    "weeks": "Week 8",
                    "topics": [
                        {"topic": "mixed", "subtopics": ["all"], "difficulty": "intermediate"}
                    ]
                }
            ],
            "total_weeks": 8,
            "description": "Structured 8-week curriculum covering all topics from basic to intermediate level"
        }
