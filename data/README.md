# Plutus Backend - CSV Data Schema Documentation

## 📊 CSV File Structures (Simplified Backend)

### 1. users.csv
**Purpose**: Store user account information for the simplified banking system
```
user_id,username,account_number,balance,daily_limit,created_at
```

**Fields**:
- `user_id`: Unique user identifier (USR + 8 digits)
- `username`: User's display name/identifier
- `account_number`: User's bank account number (16 digits)
- `balance`: Current account balance (float, default: 5000.0)
- `daily_limit`: Daily transaction limit (float, default: 10000.0)
- `created_at`: Account creation timestamp (ISO format)

**Note**: No authentication - simplified system uses direct user_id access

### 2. beneficiaries.csv
**Purpose**: Store beneficiary relationships for money transfers
```
owner_user_id,beneficiary_id,name,account_number,added_at
```

**Fields**:
- `owner_user_id`: User ID who owns this beneficiary
- `beneficiary_id`: Unique beneficiary identifier (BEN + 8 digits)
- `name`: Beneficiary's display name (used by chatbot)
- `account_number`: Beneficiary's account number (16 digits)
- `added_at`: When beneficiary was added (ISO format)

**Note**: No bank_name field - simplified to just account numbers

### 3. transactions.csv
**Purpose**: Store all financial transaction records
```
transaction_id,from_user_id,to_user_id,amount,description,timestamp
```

**Fields**:
- `transaction_id`: Unique transaction identifier (TXN + timestamp-based)
- `from_user_id`: Sender's user ID
- `to_user_id`: Receiver's user ID (optional - can be external)
- `amount`: Transaction amount (float)
- `description`: Transaction description/memo
- `timestamp`: Transaction timestamp (ISO format)

**Note**: Simplified structure - removed account numbers, status, daily totals

### 4. audit_logs.csv
**Purpose**: System activity audit trail
```
log_id,user_id,action,details,timestamp,request_id
```

**Fields**:
- `log_id`: Unique log identifier (auto-generated)
- `user_id`: User who performed the action
- `action`: Type of action (balance_check, transfer, add_beneficiary)
- `details`: JSON string with action details
- `timestamp`: When action occurred (ISO format)
- `request_id`: Request identifier for tracking

**Note**: Simplified - removed IP address tracking

## 🔄 Simplified Data Flow Examples

### Balance Check Flow (Chatbot):
```
Input: user_id = "USR12345678"
Process: Read users.csv, find user
Output: Current balance
```

### Money Transfer Flow (Chatbot):
```
Input: user_id = "USR12345678", recipient_name = "Zunaira", amount = 500
Process: 
1. Check beneficiaries.csv for "Zunaira" 
2. Get recipient account from beneficiary record
3. Update sender balance in users.csv
4. Add transaction to transactions.csv
5. Log action in audit_logs.csv
Output: Transfer confirmation
```

### Add Beneficiary Flow (Chatbot):
```
Input: user_id = "USR12345678", name = "Ali", account = "1234567890123456"
Process:
1. Generate beneficiary_id
2. Add to beneficiaries.csv
3. Log action in audit_logs.csv
Output: Beneficiary added confirmation
```

## 🤖 Chatbot Integration

The CSV structure is optimized for chatbot interactions:

**Supported Chatbot Commands**:
- `"Check balance"` → Returns user balance
- `"Send 500 to Zunaira"` → Transfer money to beneficiary
- `"Add beneficiary Ali with account 1234567890123456"` → Add new beneficiary

**Chatbot Benefits**:
- No authentication needed (direct user_id)
- Simple name-based beneficiary lookup
- Clear transaction descriptions
- Instant balance updates

## 📝 Sample Data Structure

### Sample Users:
- `USR12345678`: hamza_dev (Balance: 4068.5)
- `USR87654321`: zunaira_user (Balance: 5500.0)
- `USR11223344`: ali_hassan (Balance: 3200.0)

### Sample Beneficiaries:
- Hamza → Zunaira, Ali, Amna
- Zunaira → Hamza, Ali
- Ali → Hamza, Zunaira

### Sample Transactions:
- Regular transfers between users
- Various amounts (100-2000 range)
- Descriptive transaction messages

## � API Integration

**CSV File Usage by API Endpoints**:
- `/api/balance/{user_id}` → reads users.csv
- `/api/transfer` → reads beneficiaries.csv, updates users.csv, writes transactions.csv
- `/api/beneficiaries/{user_id}` → reads beneficiaries.csv
- `/api/add-beneficiary` → writes beneficiaries.csv

**File Management**:
- Automatic CSV file creation if missing
- Header validation on startup
- Concurrent read/write handling
- Data persistence across container restarts
