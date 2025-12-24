import { VisaLoadingAnimation } from '@/components/report/VisaLoadingState';

export default function TripReportLoading() {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center">
      <VisaLoadingAnimation />
    </div>
  );
}
