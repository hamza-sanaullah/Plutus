# Plutus Backend - CSV Data Schema Documentation

## 📊 CSV File Structures

### 1. users.csv
**Purpose**: Store user account information and authentication data
```
user_id,username,hashed_password,account_number,balance,daily_limit,created_at
```

**Fields**:
- `user_id`: Unique user identifier (USR + 8 chars)
- `username`: User's login username
- `hashed_password`: Bcrypt hashed password
- `account_number`: User's bank account number (user-provided)
- `balance`: Current account balance (float)
- `daily_limit`: Daily transaction limit (float)
- `created_at`: Account creation timestamp (ISO format)

### 2. beneficiaries.csv
**Purpose**: Store beneficiary relationships for money transfers
```
owner_user_id,beneficiary_id,name,bank_name,account_number,added_at
```

**Fields**:
- `owner_user_id`: User ID who owns this beneficiary
- `beneficiary_id`: Unique beneficiary identifier (BEN + 8 chars)
- `name`: Beneficiary's display name
- `bank_name`: Beneficiary's bank name
- `account_number`: Beneficiary's account number
- `added_at`: When beneficiary was added (ISO format)

### 3. transactions.csv
**Purpose**: Store all financial transaction records
```
transaction_id,from_user_id,to_user_id,from_account,to_account,amount,status,description,timestamp,daily_total_sent
```

**Fields**:
- `transaction_id`: Unique transaction identifier (TXN + timestamp + random)
- `from_user_id`: Sender's user ID
- `to_user_id`: Receiver's user ID
- `from_account`: Sender's account number
- `to_account`: Receiver's account number
- `amount`: Transaction amount (float)
- `status`: Transaction status (pending/success/failed)
- `description`: Transaction description/memo
- `timestamp`: Transaction timestamp (ISO format)
- `daily_total_sent`: Running total sent by user today

### 4. audit_logs.csv
**Purpose**: Audit trail for all system activities
```
log_id,user_id,action,details,timestamp,ip_address,request_id
```

**Fields**:
- `log_id`: Unique log identifier
- `user_id`: User who performed the action
- `action`: Type of action performed
- `details`: JSON string with action details
- `timestamp`: When action occurred (ISO format)
- `ip_address`: User's IP address
- `request_id`: Request identifier for tracking

## 🔄 Data Flow Examples

### User Registration Flow:
1. User provides: username, password, account_number
2. System generates: user_id, hashed_password, created_at
3. Default values: balance=1000.00, daily_limit=10000.00
4. Record added to users.csv

### Transaction Flow:
1. User: "Send 500 to Zunaira"
2. System checks beneficiaries.csv for "Zunaira"
3. If found: proceed with transaction
4. If not found: return "Beneficiary not found"
5. Transaction record added to transactions.csv
6. Audit log added to audit_logs.csv

### Beneficiary Addition Flow:
1. Chatbot provides: name, bank_name, account_number
2. System generates: beneficiary_id, added_at
3. Record added to beneficiaries.csv
4. Audit log added to audit_logs.csv

## 🔐 Security Notes

- Passwords are hashed using bcrypt
- Account numbers are user-provided and validated
- All financial operations are logged for audit
- Daily limits are enforced per user
- IP addresses tracked for security monitoring

## 📝 Sample Data Notes

The sample data includes:
- 5 test users with realistic Pakistani names
- Various bank account numbers
- Beneficiary relationships between users
- Transaction history with different statuses
- Comprehensive audit logs
- Realistic balances and daily limits
