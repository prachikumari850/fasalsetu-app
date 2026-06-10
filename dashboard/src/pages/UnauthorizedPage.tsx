import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/Button';
export function UnauthorizedPage() {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-4">
      <p className="text-5xl font-bold text-ink">403</p>
      <p className="text-ink-secondary">You don't have permission to view this page.</p>
      <Button onClick={() => navigate(-1)} variant="outlined" fullWidth={false}>Go Back</Button>
    </div>
  );
}