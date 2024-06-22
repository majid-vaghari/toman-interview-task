# Toman Backend Interview Task Documentation

## Project Overview

The Toman Backend Interview Task involves implementing a simplified wallet service with functionalities to deposit into the wallet and schedule withdrawals. Each withdrawal request is processed at a future timestamp and involves interaction with a third-party service to transfer the amount to the wallet owner's account. The solution is built using Django and includes handling concurrent transactions, validating balances at the scheduled withdrawal time, and managing possible failures in third-party service interactions.

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Models](#models)
3. [Views and URLs](#views-and-urls)
4. [Serializers](#serializers)
5. [Tasks and Scheduling](#tasks-and-scheduling)
6. [Third-Party Service Interaction](#third-party-service-interaction)
7. [Error Handling](#error-handling)
8. [Running the Project](#running-the-project)
9. [Testing](#testing)
10. [Future Improvements and Suggestions](#future-improvements-and-suggestions)

---

## Project Structure

The project is organized into multiple directories and files, each serving a specific purpose. Here's an overview:

- **`Makefile`**: make instructions for running the project in dev mode.
- **`compose.yaml`**: Docker compose file to set up and run the services.
- **`dev.env`**: Environment variables for development.
- **`configs/`**: Configuration files, including NGINX configuration.
- **`transaction-service/`**: Contains code for the third-party service.
  - `app.py`: Main application script.
  - `requirements.txt`: Dependencies for the third-party service.
- **`wallet/`**: Main Django project directory.
  - `manage.py`: Django management script.
  - `requirements.txt`: Dependencies for the Django project.
  - `transactions/`: Contains the core functionality for the wallet service.
    - `models.py`: Defines the database models.
    - `views.py`: API views for handling requests.
    - `serializers.py`: Serializers for model data.
    - `tasks.py`: Celery tasks for scheduling withdrawals.
    - `signals.py`: Signal handlers for model events.
    - `validators.py`: Custom validators for withdrawal requests.
    - `urls.py`: URL routing for the transactions app.
    - `tests/`: Contains unit tests for various components.
  - `wallet/`: Django project settings and configuration.
    - `settings.py`: Project settings.
    - `celery.py`: Celery configuration.
    - `urls.py`: URL routing for the project.

---

## Models

The core models for the wallet service are defined in `transactions/models.py`. The primary models include:

- **Wallet**: Represents a user's wallet with fields for the balance.
- **Transaction**: Represents a transaction with fields for amount, type (deposit/withdrawal), status, and scheduled timestamp.

```python
class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=TRANSACTION_STATUS_CHOICES)
    scheduled_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## Views and URLs

The views handle API requests for creating deposits and scheduling withdrawals. They are defined in `transactions/views.py` and routed through `transactions/urls.py`.

- **DepositView**: Handles deposit requests.
- **WithdrawalView**: Handles withdrawal scheduling requests.

```python
from rest_framework import generics

class DepositView(generics.CreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = DepositSerializer

class WithdrawalView(generics.CreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = WithdrawalSerializer
```

URLs configuration in `transactions/urls.py`:

```python
from django.urls import path
from .views import DepositView, WithdrawalView

urlpatterns = [
    path('deposit/', DepositView.as_view(), name='deposit'),
    path('withdraw/', WithdrawalView.as_view(), name='withdraw'),
]
```

---

## Serializers

Serializers convert complex data types to native Python datatypes that can be easily rendered into JSON. Defined in `transactions/serializers.py`:

- **DepositSerializer**: Serializes deposit data.
- **WithdrawalSerializer**: Serializes withdrawal data and includes validation logic.

```python
from rest_framework import serializers

class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['wallet', 'amount']

class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['wallet', 'amount', 'scheduled_time']
```

---

## Tasks and Scheduling

Celery is used for scheduling withdrawal transactions. Tasks are defined in `transactions/tasks.py`.

- **process_withdrawal**: Task to process a withdrawal at the scheduled time.


---

## Third-Party Service Interaction

The `transaction-service/app.py` handles interaction with the third-party service. The service may fail, and such cases need to be handled gracefully.

- **send_request**: Function to send a request to the third-party service.

```python
import requests

def send_request(transaction):
    try:
        response = requests.post('http://third-party-service/endpoint', data=transaction)
        if response.status_code == 200:
            return True
    except requests.exceptions.RequestException:
        return False
    return False
```

---

## Error Handling

Error handling ensures the system remains robust and resilient to failures.

- **Transaction Failures**: If a third-party service request fails, the transaction is marked as failed, and the amount is returned to the wallet.

```python
def process_withdrawal(transaction_id):
    transaction = Transaction.objects.get(id=transaction_id)
    if send_request(transaction):
        transaction.status = 'completed'
    else:
        transaction.status = 'failed'
        transaction.wallet.balance += transaction.amount
    transaction.save()
```

---

## Running the Project

To run the project, you should have docker compose and make installed, follow these steps:

1. **Clone the repository**:
    ```sh
    git clone <repository_url>
    cd toman-task
    ```

2. **Set up Docker**:
    ```sh
    make
    ```

3. **Access the service**:
    The service should be running at `http://localhost`.

---

## Testing

Unit tests are located in `transactions/tests/`. To run tests:

```sh
docker-compose exec wallet python manage.py test
```

Tests cover various components:

- **Task Tests**: Test withdrawal processing tasks.
- **Validator Tests**: Test custom validators for transactions.

---

## Future Improvements and Suggestions

### 1. Resolve Lazy Text Object Evaluation Issue
There is a known issue in Django regarding the unnecessary evaluation of lazy text objects in min/max value validators. A pull request has been submitted to address this problem. Once the pull request is merged, it should be incorporated into the project to ensure better performance and reliability. 

- **Pull Request**: [Django PR #18284](https://github.com/django/django/pull/18284)

### 2. Code Quality and Consistency
To maintain high code quality and consistency across the project, it's recommended to add settings for `pylint` and `autopep8`. These tools help enforce coding standards and automate code formatting, ensuring that all code adheres to the same style guide.

### 3. Web Interface for Accessibility
While the current implementation focuses on API endpoints, adding a web interface can enhance accessibility. This interface can include forms for deposits and withdrawals and a read-only section displaying transaction details. This would be beneficial for debugging and provide a user-friendly way to interact with the service.

### 4. Implement `get_absolute_url` for Models
Implementing the `get_absolute_url` method for models can help generate canonical URLs for model instances. This is particularly useful for linking to specific transactions or wallets directly from the web interface or other parts of the application.

```python
class Wallet(models.Model):
    # existing fields

    def get_absolute_url(self):
        return reverse('wallet_detail', args=[str(self.id)])
```

### 5. Increase Maximum Digit Limitation
Currently, the maximum digit limitation for balance and transaction amounts is set to 10 digits. Depending on the use case and future requirements, this limit can be increased to accommodate larger transactions and balances.

### 6. Support for Multiple Currencies
To make the wallet service more versatile, adding support for multiple currencies is a crucial improvement. This can be achieved by adding a currency field to the Wallet and Transaction models and performing currency conversions as necessary.

```python
class Wallet(models.Model):
    # existing fields
    currency = models.CharField(max_length=3, default='USD')

class Transaction(models.Model):
    # existing fields
    currency = models.CharField(max_length=3, default='USD')
```

### 7. Enhance Django Admin
Improving the Django admin interface can significantly enhance the ease of managing transactions and wallets. Custom admin forms and templates can provide more control and better visualization of the data.

```python
from django.contrib import admin
from .models import Wallet, Transaction

class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'currency')
    search_fields = ('user__username',)

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'amount', 'transaction_type', 'status', 'scheduled_time')
    list_filter = ('transaction_type', 'status')
    search_fields = ('wallet__user__username',)

admin.site.register(Wallet, WalletAdmin)
admin.site.register(Transaction, TransactionAdmin)
```

### 8. Implement Retry Policy for Celery Tasks
To handle failures in Celery tasks more robustly, implementing a retry policy is essential. This ensures that tasks are retried in case of transient errors, improving the reliability of scheduled withdrawals.

```python
@shared_task(bind=True, max_retries=3)
def process_withdrawal(self, transaction_id):
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        # Logic to process the withdrawal
    except Exception as exc:
        raise self.retry(exc=exc)
```

### 9. Add DurationField to WithdrawalRequestSerializer
Adding a `DurationField` to the `WithdrawalRequestSerializer` can allow users to specify a delay for withdrawals instead of an exact timestamp. This can provide more flexibility in scheduling future transactions.

```python
class WithdrawalRequestSerializer(serializers.ModelSerializer):
    delay = serializers.DurationField()

    class Meta:
        model = Transaction
        fields = ['wallet', 'amount', 'delay']
```

### 10. Improved Logging and Monitoring
Implement comprehensive logging and monitoring to track the system's performance and identify issues in real-time. Integrate tools like Prometheus and Grafana for monitoring and alerting.

### 11. Automated Testing and Continuous Integration
Set up continuous integration (CI) with automated testing to ensure code quality and catch issues early. Tools like GitHub Actions, Travis CI, or Jenkins can be used to automate the testing process.

### 12. API Rate Limiting and Throttling
Implement rate limiting and throttling for the API endpoints to prevent abuse and ensure fair usage among users. Django REST framework provides built-in support for this.

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '1000/day',
    }
}
```

### 13. Websockets for Real-Time Updates
Incorporate WebSocket support to provide real-time updates to users about their transactions and wallet balance changes. Django Channels can be used to implement WebSocket support.

### 14. Scalability Improvements
To handle increased load, consider implementing horizontal scaling using Kubernetes or Docker Swarm. This will ensure the service can handle a growing number of users and transactions.

### 15. Enhanced Security Measures
Implement additional security measures such as rate limiting, IP whitelisting, and audit logs to track changes and access to the system. Ensuring compliance with security best practices will help protect user data.

### 16. User Notifications
Add user notification support via email or SMS for important events such as successful deposits, scheduled withdrawals, and failed transactions. This can enhance user experience and keep users informed about their account activity.

```python
from django.core.mail import send_mail

def notify_user(transaction):
    send_mail(
        'Transaction Update',
        f'Your transaction {transaction.id} status is {transaction.status}',
        'from@example.com',
        [transaction.wallet.user.email],
        fail_silently=False,
    )
```
