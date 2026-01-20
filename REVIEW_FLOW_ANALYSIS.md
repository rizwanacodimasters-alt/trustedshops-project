# REVIEW FLOW ANALYSIS - Current Implementation

## Current State Analysis

### 1. Review Form & Submission Logic

**Frontend:**
- Location: `/app/frontend/src/pages/ShopDetail.jsx`
- Current behavior:
  - Review form allows rating selection (1-5 stars)
  - Comment field (required, min 10 chars)
  - Submit button
  - **NO evidence upload UI exists yet**

**Key Finding:** Review submission form does NOT have file upload functionality in the frontend.

---

### 2. Backend Review Creation

**Location:** `/app/backend/routes/review_routes.py`

**Current Flow:**
```python
POST /api/reviews
- Validates rating (1-5)
- Validates comment (min 10 chars)
- Checks content filters
- Determines if proof required: rating <= 2  # CURRENT: Only 1-2 stars
- Sets status: "pending" if rating <= 2, else "published"
```

**Key Finding:** 
- Current threshold: `rating <= 2` (only 1-2 stars require proof)
- **NEEDS TO CHANGE TO:** `rating <= 3` (1-2-3 stars require proof)

---

### 3. File Upload Implementation

**Location:** `/app/backend/routes/proof_upload_routes.py`

**Current Proof Upload System:**
```python
POST /api/reviews/{review_id}/upload-proof
- Accepts: proof_photos (list of base64), proof_chat_history, proof_order_number
- Current requirements:
  - 1-5 photos (base64)
  - Chat history (base64 file)
  - Order number
```

**Key Findings:**
- ✅ Upload route exists
- ✅ Base64 encoding used
- ❌ NO file size validation (10 MB limit missing)
- ❌ NO file type validation (image-only check missing)
- ❌ NO server-side security checks
- ❌ Two-step process: Create review first, then upload proof separately

**Problem:** Current system requires user to:
1. Submit review → gets "pending" status
2. Then upload proof via separate API call

**Required Change:** Make proof upload part of review creation (one-step process)

---

### 4. Validation Rules

**Frontend Validation:**
- Location: `/app/frontend/src/utils/validation.js`
- Current: Email, password, name, phone, URL validation
- **MISSING:** File upload validation

**Backend Validation:**
- Location: `/app/backend/utils/content_filter.py`
- Function: `validate_proof_data()`
- Current checks:
  - Photo count (1-5)
  - Chat history exists
  - Order number min 3 chars
  - Basic base64 format check
- **MISSING:**
  - File size limit (10 MB per file)
  - File type validation (JPG, PNG, WEBP only)
  - Total upload size limit
  - Image dimension validation

---

### 5. Review Status & Admin Approval

**Current Implementation:**
- Status field exists: "pending", "approved", "rejected", "published"
- Admin approval route exists: `POST /api/admin/reviews/{id}/action`
- Admin UI exists: `/app/frontend/src/components/admin/AdminReviews.jsx`

**Current Behavior:**
- Reviews with rating <= 2 → status = "pending"
- Reviews with rating > 2 → status = "published"

**Required Change:**
- Reviews with rating <= 3 → status = "pending" (with proof)
- Reviews with rating > 3 → status = "published" (no proof)

---

### 6. Security Issues Found

**Critical Security Gaps:**

1. **NO Server-Side File Validation:**
   - Base64 strings accepted without checking actual file size
   - No validation of file type
   - No malware/executable check
   - No file name sanitization

2. **Frontend-Only Validation:**
   - Easy to bypass via curl/Postman
   - No backend enforcement

3. **Base64 Storage:**
   - Large base64 strings stored directly in MongoDB
   - No compression
   - No CDN/S3 integration
   - Potential database bloat

4. **No Rate Limiting:**
   - Users could upload unlimited files
   - No upload quota per user

---

### 7. What Needs to Change

#### Backend Changes Required:

1. **Review Creation Logic** (`review_routes.py`):
   ```python
   # Change from:
   requires_proof = should_require_proof(review_data.rating)  # rating <= 2
   
   # To:
   requires_proof = should_require_proof(review_data.rating)  # rating <= 3
   ```

2. **Content Filter Update** (`content_filter.py`):
   ```python
   def should_require_proof(rating: int) -> bool:
       return rating <= 3  # Changed from <= 2
   ```

3. **New File Validation** (`content_filter.py`):
   ```python
   def validate_image_file(base64_string: str) -> bool:
       # Check file size (max 10 MB)
       # Check file type (JPG, PNG, WEBP only)
       # Validate base64 format
       # Check for executable content
       # Sanitize metadata
   ```

4. **Review Model Update** (`models.py`):
   ```python
   class ReviewCreate(ReviewBase):
       order_id: Optional[str] = None
       order_reference: Optional[str] = None
       proof_photos: Optional[List[str]] = []  # Make required if rating <= 3
       proof_order_number: Optional[str] = None  # Make required if rating <= 3
   ```

5. **Combined Submission** (new approach):
   - Allow proof upload during review creation
   - Validate evidence BEFORE creating review
   - Atomic operation: create review + proof in one transaction

#### Frontend Changes Required:

1. **Review Form Component** (ShopDetail.jsx or new component):
   - Add conditional evidence section
   - Show when rating <= 3
   - Hide when rating > 3
   - Fields:
     - Order number input (required)
     - Image upload (multiple files, min 1 required)
     - Preview uploaded images
     - Clear/remove uploaded images

2. **File Upload Component** (new):
   ```jsx
   <FileUpload
     accept="image/jpeg,image/png,image/webp"
     maxSize={10 * 1024 * 1024}  // 10 MB
     maxFiles={5}
     required={rating <= 3}
     onChange={handleFileUpload}
   />
   ```

3. **Validation Logic**:
   - Check file type before upload
   - Check file size before base64 conversion
   - Show preview
   - Show error messages
   - Prevent form submission if invalid

4. **Conditional Rendering**:
   ```jsx
   {rating <= 3 && (
     <div className="evidence-section">
       <OrderNumberInput required />
       <ImageUpload required minFiles={1} maxFiles={5} />
     </div>
   )}
   ```

---

### 8. Implementation Priority

**Phase 1 - Backend Security (Critical):**
1. Update `should_require_proof()` to use `<= 3`
2. Implement file size validation (10 MB limit)
3. Implement file type validation (images only)
4. Add security checks (no executables)
5. Update review creation to accept proof in single request

**Phase 2 - Frontend UI (High):**
1. Create FileUpload component
2. Add conditional evidence section to review form
3. Implement client-side validation
4. Add image preview
5. Update form submission logic

**Phase 3 - Admin Panel (Medium):**
1. Update admin panel to show 1-3 star reviews (not just 1-2)
2. Display order number in admin view
3. Improve image preview in admin panel

**Phase 4 - Testing (Critical):**
1. Test file upload with various file types
2. Test file size limits
3. Test bypass attempts (curl, dev tools)
4. Test admin approval workflow

---

## Summary of Changes Needed

### Backend:
- ✅ Proof upload routes exist
- ❌ Need to change threshold from 2 to 3 stars
- ❌ Need file size validation (10 MB)
- ❌ Need file type validation (images only)
- ❌ Need security validation (no executables)
- ❌ Need combined submission (review + proof in one call)
- ❌ Need to make order_number required for rating <= 3

### Frontend:
- ❌ NO review submission form with file upload exists
- ❌ Need to create FileUpload component
- ❌ Need to add conditional evidence section
- ❌ Need client-side validation
- ❌ Need image preview
- ❌ Need to update ShopDetail.jsx or create new ReviewSubmission component

### Security:
- ❌ Server-side validation missing
- ❌ File size check missing
- ❌ File type check missing
- ❌ Malware scan missing
- ❌ Rate limiting missing

---

## Recommended Implementation Approach

**Option 1: Extend Existing System (Recommended)**
- Keep base64 storage (simple, no external dependencies)
- Add validation layers
- Improve security checks
- Change threshold to 3 stars
- Add frontend UI

**Option 2: Migrate to File Storage**
- Switch to S3 or local file storage
- Store URLs instead of base64
- More scalable but requires infrastructure changes
- More complex implementation

**Recommended:** Option 1 for now (MVP approach), Option 2 for production scaling.

---

## Ready to Implement?

All analysis complete. Ready to proceed with implementation once confirmed.
