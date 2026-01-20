import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import { Button } from '../ui/button';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Input } from '../ui/input';
import { ImageUpload } from '../ui/image-upload';
import { Star, Loader2, AlertCircle, FileText } from 'lucide-react';
import { useToast } from '../../hooks/use-toast';
import { reviewAPI } from '../../services/api';

const EditReviewDialog = ({ open, onClose, review, onSuccess }) => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    rating: review?.rating || 5,
    comment: review?.comment || '',
    proof_photos: review?.proof_photos || [],
    proof_order_number: review?.proof_order_number || ''
  });
  
  // Reset form data when review changes or dialog opens
  useEffect(() => {
    if (review && open) {
      setFormData({
        rating: review.rating || 5,
        comment: review.comment || '',
        proof_photos: review.proof_photos || [],
        proof_order_number: review.proof_order_number || ''
      });
    }
  }, [review, open]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (formData.comment.length < 10) {
      toast({
        title: 'Fehler',
        description: 'Kommentar muss mindestens 10 Zeichen lang sein',
        variant: 'destructive'
      });
      return;
    }
    
    // Validate proof for low-star reviews (1-3 stars)
    if (formData.rating <= 3) {
      if (!formData.proof_order_number || formData.proof_order_number.length < 3) {
        toast({
          title: 'Bestellnummer erforderlich',
          description: 'Für Bewertungen mit 1-3 Sternen ist eine Bestellnummer erforderlich.',
          variant: 'destructive',
        });
        return;
      }
      
      if (!formData.proof_photos || formData.proof_photos.length === 0) {
        toast({
          title: 'Fotos erforderlich',
          description: 'Für Bewertungen mit 1-3 Sternen ist mindestens 1 Foto erforderlich.',
          variant: 'destructive',
        });
        return;
      }
    }

    setLoading(true);
    try {
      // Prepare update data
      const updateData = {
        rating: formData.rating,
        comment: formData.comment
      };
      
      // Include proof data if rating is 1-3 stars
      if (formData.rating <= 3) {
        updateData.proof_photos = formData.proof_photos;
        updateData.proof_order_number = formData.proof_order_number;
      }
      
      await reviewAPI.updateReview(review.id, updateData);
      
      const statusMessage = formData.rating <= 3
        ? 'Ihre Bewertung wurde aktualisiert und wartet auf erneute Prüfung durch den Administrator.'
        : 'Ihre Bewertung wurde erfolgreich aktualisiert.';
      
      toast({
        title: 'Erfolg!',
        description: statusMessage
      });
      
      onSuccess();
      onClose();
    } catch (error) {
      toast({
        title: 'Fehler',
        description: error.response?.data?.detail || 'Bewertung konnte nicht aktualisiert werden',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[525px]">
        <DialogHeader>
          <DialogTitle>Bewertung bearbeiten</DialogTitle>
          <DialogDescription>
            {review?.shop_name}
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Rating */}
          <div className="space-y-2">
            <Label>Bewertung</Label>
            <div className="flex gap-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onClick={() => setFormData({ ...formData, rating: star })}
                  className="hover:scale-110 transition-transform"
                >
                  <Star
                    className={`w-8 h-8 ${
                      star <= formData.rating
                        ? 'fill-yellow-400 text-yellow-400'
                        : 'text-gray-300'
                    }`}
                  />
                </button>
              ))}
            </div>
          </div>

          {/* Comment */}
          <div className="space-y-2">
            <Label htmlFor="comment">Ihr Kommentar</Label>
            <Textarea
              id="comment"
              value={formData.comment}
              onChange={(e) => setFormData({ ...formData, comment: e.target.value })}
              placeholder="Teilen Sie Ihre Erfahrungen..."
              rows={5}
              minLength={10}
              maxLength={1000}
              required
            />
            <p className="text-sm text-gray-500">
              {formData.comment.length}/1000 Zeichen (min. 10)
            </p>
          </div>
          
          {/* Proof Section for Low-Star Reviews (1-3 stars) */}
          {formData.rating <= 3 && (
            <div className="p-4 bg-amber-50 border-2 border-amber-300 rounded-lg space-y-4">
              <div className="flex items-start gap-2">
                <div className="p-2 bg-amber-100 rounded-full">
                  <AlertCircle className="w-5 h-5 text-amber-600" />
                </div>
                <div>
                  <p className="font-medium text-amber-900">Nachweis erforderlich</p>
                  <p className="text-sm text-amber-700 mt-1">
                    Für Bewertungen mit 1-3 Sternen benötigen wir einen Kaufnachweis. 
                    Ihre Bewertung wird nach der Prüfung durch unsere Administratoren veröffentlicht.
                  </p>
                </div>
              </div>
              
              <div className="space-y-4">
                <div>
                  <Label htmlFor="order_number">
                    Bestellnummer <span className="text-red-500">*</span>
                  </Label>
                  <Input
                    id="order_number"
                    value={formData.proof_order_number}
                    onChange={(e) => setFormData({ ...formData, proof_order_number: e.target.value })}
                    placeholder="z.B. ORD-2024-12345"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Die Bestellnummer finden Sie in Ihrer Bestellbestätigung
                  </p>
                </div>
                
                <div>
                  <ImageUpload
                    value={formData.proof_photos}
                    onChange={(photos) => setFormData({ ...formData, proof_photos: photos })}
                    maxFiles={5}
                    maxSizeMB={10}
                    required={formData.rating <= 3}
                    label="Produktfotos als Nachweis"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Fotos der Bestellung, Rechnung oder des Produkts (JPG, PNG, WEBP - max. 10 MB pro Bild)
                  </p>
                </div>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={loading}
            >
              Abbrechen
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Wird gespeichert...
                </>
              ) : (
                'Speichern'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default EditReviewDialog;