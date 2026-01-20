import React, { useState } from 'react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '../ui/alert-dialog';
import { Loader2 } from 'lucide-react';
import { useToast } from '../../hooks/use-toast';
import { reviewAPI } from '../../services/api';

const DeleteReviewDialog = ({ open, onClose, review, onSuccess }) => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);

  const handleDelete = async () => {
    setLoading(true);
    try {
      await reviewAPI.deleteReview(review.id);
      
      toast({
        title: 'Erfolg!',
        description: 'Ihre Bewertung wurde gelöscht'
      });
      
      onSuccess();
      onClose();
    } catch (error) {
      toast({
        title: 'Fehler',
        description: error.response?.data?.detail || 'Bewertung konnte nicht gelöscht werden',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <AlertDialog open={open} onOpenChange={onClose}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Bewertung löschen?</AlertDialogTitle>
          <AlertDialogDescription>
            Möchten Sie Ihre Bewertung für <strong>{review?.shop_name}</strong> wirklich löschen?
            Diese Aktion kann nicht rückgängig gemacht werden.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={loading}>Abbrechen</AlertDialogCancel>
          <AlertDialogAction
            onClick={handleDelete}
            disabled={loading}
            className="bg-red-600 hover:bg-red-700"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Wird gelöscht...
              </>
            ) : (
              'Löschen'
            )}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
};

export default DeleteReviewDialog;