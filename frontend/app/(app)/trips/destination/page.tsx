import DestinationIntelligencePage from '@/components/destination/DestinationIntelligencePage';
import { sampleDestinationData } from '@/lib/mock-data/destination-sample';

export const metadata = {
  title: 'Destination Intelligence - Japan | TIP',
  description:
    'Comprehensive destination intelligence for Japan including weather, culture, safety, and more.',
};

export default function DestinationDemoPage() {
  return (
    <DestinationIntelligencePage
      data={sampleDestinationData}
      callbacks={{
        onCardExpand: (cardId) => console.log('Card expanded:', cardId),
        onCardCollapse: (cardId) => console.log('Card collapsed:', cardId),
        onExternalLinkClick: (url, title) => console.log('External link clicked:', title, url),
      }}
      allowMultipleExpanded={true}
    />
  );
}
