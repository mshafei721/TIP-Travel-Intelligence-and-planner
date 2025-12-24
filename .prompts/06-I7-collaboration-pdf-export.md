# I7: Collaboration & PDF Export

> **Prerequisites**: Read `00-session-context.md` first

## Objective

Enable trip sharing, collaboration features, and PDF export for offline access.

## Current Status

| Feature | Frontend | Backend | Status |
|---------|----------|---------|--------|
| Share Link | 0% | 0% | Not Started |
| Invite Collaborators | 0% | 0% | Not Started |
| Permissions | 0% | 0% | Not Started |
| Comments | 0% | 0% | Not Started |
| PDF Export | 0% | 0% | Not Started |
| Print View | 0% | - | Not Started |

---

## BACKEND TASKS

### API Endpoints

```python
# backend/app/api/sharing.py

# Share links
POST /api/trips/{id}/share              # Generate share link
GET  /api/trips/{id}/share              # Get share settings
PUT  /api/trips/{id}/share              # Update share settings
DELETE /api/trips/{id}/share            # Revoke share link

# Collaborators
GET  /api/trips/{id}/collaborators      # List collaborators
POST /api/trips/{id}/collaborators      # Invite collaborator
PUT  /api/trips/{id}/collaborators/{user_id}  # Update permissions
DELETE /api/trips/{id}/collaborators/{user_id}  # Remove collaborator

# Comments
GET  /api/trips/{id}/comments           # List comments
POST /api/trips/{id}/comments           # Add comment
PUT  /api/trips/{id}/comments/{comment_id}  # Edit comment
DELETE /api/trips/{id}/comments/{comment_id}  # Delete comment

# Export
GET  /api/trips/{id}/export/pdf         # Generate PDF
GET  /api/trips/{id}/export/json        # Export as JSON
```

### Data Models

```python
# backend/app/models/sharing.py

class ShareSettings(BaseModel):
    trip_id: str
    is_public: bool = False
    share_token: str | None
    share_url: str | None
    expires_at: datetime | None
    allow_comments: bool = True
    allow_copy: bool = False

class Collaborator(BaseModel):
    user_id: str
    trip_id: str
    email: str
    name: str
    role: str  # viewer, editor, owner
    invited_at: datetime
    accepted_at: datetime | None

class Comment(BaseModel):
    id: str
    trip_id: str
    user_id: str
    user_name: str
    content: str
    section: str | None  # which section comment is on
    created_at: datetime
    updated_at: datetime
```

### PDF Generation

```python
# backend/app/services/pdf_generator.py

from weasyprint import HTML, CSS
from jinja2 import Template

class PDFGenerator:
    def __init__(self, trip: Trip, report: TripReport):
        self.trip = trip
        self.report = report

    def generate(self) -> bytes:
        """Generate PDF from trip report"""
        # 1. Render HTML template
        html_content = self.render_template()

        # 2. Apply CSS styles
        css = CSS(string=self.get_styles())

        # 3. Generate PDF
        pdf = HTML(string=html_content).write_pdf(stylesheets=[css])

        return pdf

    def render_template(self) -> str:
        template = Template(self.get_template())
        return template.render(
            trip=self.trip,
            report=self.report,
            generated_at=datetime.utcnow()
        )
```

---

## FRONTEND TASKS

### Components to Build

```
frontend/components/sharing/
├── ShareDialog.tsx           # Share modal
├── ShareLinkInput.tsx        # Copy share link
├── PermissionSelect.tsx      # Role dropdown
├── CollaboratorList.tsx      # List of collaborators
├── CollaboratorInvite.tsx    # Invite form
├── CollaboratorCard.tsx      # Single collaborator
├── CommentSection.tsx        # Comments list
├── CommentForm.tsx           # Add comment
├── CommentCard.tsx           # Single comment
├── ExportMenu.tsx            # Export options dropdown
└── PrintStyles.tsx           # Print-specific styles
```

### Pages to Build

```
frontend/app/(app)/trips/[id]/
├── share/
│   └── page.tsx              # Sharing settings page
└── print/
    └── page.tsx              # Print-friendly view

frontend/app/shared/[token]/
└── page.tsx                  # Public shared view
```

---

## SHARE DIALOG COMPONENT

```tsx
// frontend/components/sharing/ShareDialog.tsx

export function ShareDialog({ tripId, isOpen, onClose }: Props) {
  const [settings, setSettings] = useState<ShareSettings>();
  const [collaborators, setCollaborators] = useState<Collaborator[]>([]);

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent class="max-w-lg">
        <DialogHeader>
          <DialogTitle>Share Trip</DialogTitle>
        </DialogHeader>

        <Tabs defaultValue="link">
          <TabsList>
            <TabsTrigger value="link">Share Link</TabsTrigger>
            <TabsTrigger value="people">People</TabsTrigger>
          </TabsList>

          <TabsContent value="link">
            <div class="space-y-4">
              {/* Toggle public sharing */}
              <div class="flex items-center justify-between">
                <div>
                  <p class="font-medium">Anyone with the link</p>
                  <p class="text-sm text-slate-500">
                    Anyone can view this trip
                  </p>
                </div>
                <Switch
                  checked={settings?.is_public}
                  onCheckedChange={togglePublic}
                />
              </div>

              {/* Share link */}
              {settings?.is_public && (
                <ShareLinkInput url={settings.share_url} />
              )}

              {/* Link expiry */}
              <div>
                <Label>Link expires</Label>
                <Select value={expiry} onValueChange={setExpiry}>
                  <SelectItem value="never">Never</SelectItem>
                  <SelectItem value="7d">7 days</SelectItem>
                  <SelectItem value="30d">30 days</SelectItem>
                </Select>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="people">
            <div class="space-y-4">
              {/* Invite form */}
              <CollaboratorInvite tripId={tripId} onInvite={handleInvite} />

              {/* Collaborator list */}
              <CollaboratorList
                collaborators={collaborators}
                onUpdateRole={handleUpdateRole}
                onRemove={handleRemove}
              />
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
```

---

## PDF EXPORT IMPLEMENTATION

### Backend Template

```html
<!-- backend/templates/pdf/report.html -->
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{{ trip.destination }} - Travel Report</title>
</head>
<body>
  <header>
    <h1>{{ trip.destination }}</h1>
    <p>{{ trip.departure_date }} - {{ trip.return_date }}</p>
  </header>

  <section class="visa">
    <h2>Visa Requirements</h2>
    {% if report.visa.visa_required %}
    <p class="warning">Visa Required</p>
    {% else %}
    <p class="success">Visa-Free Entry</p>
    {% endif %}
    <!-- More visa details -->
  </section>

  <section class="itinerary">
    <h2>Itinerary</h2>
    {% for day in report.itinerary.days %}
    <div class="day">
      <h3>Day {{ day.day_number }}: {{ day.title }}</h3>
      {% for activity in day.activities %}
      <div class="activity">
        <span class="time">{{ activity.start_time }}</span>
        <span class="name">{{ activity.name }}</span>
      </div>
      {% endfor %}
    </div>
    {% endfor %}
  </section>

  <footer>
    <p>Generated by TIP - Travel Intelligence & Planner</p>
    <p>{{ generated_at }}</p>
  </footer>
</body>
</html>
```

### Frontend Export Button

```tsx
// frontend/components/sharing/ExportMenu.tsx

export function ExportMenu({ tripId }: Props) {
  const [isExporting, setIsExporting] = useState(false);

  const handleExportPDF = async () => {
    setIsExporting(true);
    try {
      const response = await fetch(`/api/trips/${tripId}/export/pdf`);
      const blob = await response.blob();

      // Download file
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `trip-report-${tripId}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline">
          <Download class="w-4 h-4 mr-2" />
          Export
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem onClick={handleExportPDF} disabled={isExporting}>
          {isExporting ? <Spinner /> : <FileText class="w-4 h-4 mr-2" />}
          Download PDF
        </DropdownMenuItem>
        <DropdownMenuItem onClick={handlePrint}>
          <Printer class="w-4 h-4 mr-2" />
          Print
        </DropdownMenuItem>
        <DropdownMenuItem onClick={handleExportJSON}>
          <Code class="w-4 h-4 mr-2" />
          Export JSON
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
```

---

## TDD TEST CASES

### Backend Tests

```python
# backend/tests/api/test_sharing.py

def test_generate_share_link():
    """Should generate unique share token"""

def test_share_link_access():
    """Should allow access with valid token"""

def test_expired_share_link():
    """Should reject expired share links"""

def test_invite_collaborator():
    """Should send invitation email"""

def test_collaborator_permissions():
    """Viewer cannot edit, editor can"""

def test_pdf_generation():
    """Should generate valid PDF"""

def test_pdf_contains_all_sections():
    """PDF should include all report sections"""
```

### Frontend Tests

```typescript
describe('ShareDialog', () => {
  it('generates share link on toggle')
  it('copies link to clipboard')
  it('shows collaborator list')
  it('allows inviting by email')
})

describe('ExportMenu', () => {
  it('downloads PDF on click')
  it('shows loading state')
  it('handles export errors')
})
```

---

## IMPLEMENTATION ORDER

### Phase 1: Share Links (Day 1)
1. [ ] Backend share endpoints
2. [ ] Share token generation
3. [ ] Public view page
4. [ ] ShareDialog component

### Phase 2: Collaborators (Day 2)
1. [ ] Collaborator CRUD endpoints
2. [ ] Email invitation (optional)
3. [ ] Permission system
4. [ ] CollaboratorList component

### Phase 3: Comments (Day 3)
1. [ ] Comment endpoints
2. [ ] CommentSection component
3. [ ] Real-time updates (polling)
4. [ ] Comment notifications

### Phase 4: PDF Export (Day 4)
1. [ ] Install WeasyPrint
2. [ ] Create PDF template
3. [ ] PDF generation endpoint
4. [ ] ExportMenu component

### Phase 5: Polish (Day 5)
1. [ ] Print styles
2. [ ] Mobile responsive
3. [ ] Error handling
4. [ ] Update feature_list.json

---

## DEPENDENCIES

```txt
# Backend
weasyprint>=60.0
jinja2>=3.1.0

# Frontend (already installed)
# Uses existing Radix UI components
```

---

## DELIVERABLES

- [ ] Backend: 12+ API endpoints
- [ ] Share links with expiry
- [ ] Collaborator management
- [ ] Comments system
- [ ] PDF export (WeasyPrint)
- [ ] Print-friendly view
- [ ] Tests: >80% coverage
- [ ] feature_list.json updated
- [ ] Committed and pushed
