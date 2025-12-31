'use client';

import * as React from 'react';
import { MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { FeedbackModal, useFeedbackModal } from './FeedbackModal';

interface FeedbackButtonProps {
  variant?: 'default' | 'outline' | 'ghost';
  size?: 'default' | 'sm' | 'lg' | 'icon';
  className?: string;
}

export function FeedbackButton({ variant = 'ghost', size = 'sm', className }: FeedbackButtonProps) {
  const { isOpen, openFeedback, closeFeedback, defaultType, errorContext } = useFeedbackModal();

  return (
    <>
      <Button variant={variant} size={size} onClick={() => openFeedback()} className={className}>
        <MessageSquare className="h-4 w-4 mr-2" />
        Send Feedback
      </Button>

      <FeedbackModal
        isOpen={isOpen}
        onClose={closeFeedback}
        defaultType={defaultType}
        errorContext={errorContext}
      />
    </>
  );
}
