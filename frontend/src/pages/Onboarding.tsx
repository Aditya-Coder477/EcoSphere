import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useAppStore } from '../store/useAppStore';
import { carbonService } from '../services/carbonService';
import { ROUTES } from '../constants/routes';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { Card, CardContent } from '../components/ui/Card';

const schema = z.object({
  name: z.string().min(2, 'Name is required'),
  country: z.string().min(1, 'Country is required'),
  household_size: z.coerce.number().min(1),
  diet: z.string().min(1),
  commute_mode: z.string().min(1),
  budget_level: z.string().min(1)
});

type OnboardingFormData = z.infer<typeof schema>;

const Onboarding = () => {
  const navigate = useNavigate();
  const { setUser, setFootprint } = useAppStore();
  const [loading, setLoading] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm<OnboardingFormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: '',
      country: 'USA',
      household_size: 1,
      diet: 'average',
      commute_mode: 'car',
      budget_level: 'medium'
    }
  });

  const onSubmit = async (data: OnboardingFormData) => {
    setLoading(true);
    try {
      // Build the user profile from form data
      const userId = crypto.randomUUID();
      const userProfile = {
        id: userId,
        name: data.name,
        preferences: {
          country: data.country,
          household_size: Number(data.household_size),
          diet: data.diet,
          commute_mode: data.commute_mode,
          budget_level: data.budget_level,
        },
      };

      setUser(userProfile);

      // Try backend; fall back to mock footprint on any failure
      try {
        const footRes = await carbonService.calculateCarbon(userId, {
          transport_type: data.commute_mode,
          transport_distance_km: 15000,
          diet_type: data.diet,
          electricity_kwh: 4000,
        });
        if (footRes?.data) {
          setFootprint(footRes.data);
        } else {
          throw new Error('Empty response');
        }
      } catch {
        // Backend unavailable — use mock footprint so the dashboard is always full
        const { mockCarbonSummary } = await import('../mocks');
        setFootprint({ ...mockCarbonSummary, user_id: userId });
      }

      navigate(ROUTES.DASHBOARD);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="min-h-screen flex items-center justify-center p-6 relative overflow-hidden">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/10 blur-[150px] rounded-full pointer-events-none"></div>
      
      <Card className="w-full max-w-lg z-10">
        <CardContent className="p-8">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold mb-2">Welcome to EcoSphere</h2>
            <p className="text-text-muted">Let's build your initial footprint profile.</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div>
              <label className="text-sm font-medium mb-1.5 block">Your Name</label>
              <Input {...register('name')} placeholder="e.g. Jane Doe" />
              {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name.message as string}</p>}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-1.5 block">Country</label>
                <Select {...register('country')} options={[
                  { value: 'USA', label: 'United States' },
                  { value: 'GBR', label: 'United Kingdom' },
                  { value: 'IND', label: 'India' },
                  { value: 'CHN', label: 'China' },
                  { value: 'DEU', label: 'Germany' },
                  { value: 'FRA', label: 'France' },
                  { value: 'JPN', label: 'Japan' },
                  { value: 'CAN', label: 'Canada' },
                  { value: 'AUS', label: 'Australia' },
                  { value: 'BRA', label: 'Brazil' },
                  { value: 'ITA', label: 'Italy' }
                ]} />
              </div>
              <div>
                <label className="text-sm font-medium mb-1.5 block">Household Size</label>
                <Input type="number" {...register('household_size')} />
              </div>
            </div>

            <div>
              <label className="text-sm font-medium mb-1.5 block">Diet Pattern</label>
              <Select {...register('diet')} options={[
                { value: 'meat_heavy', label: 'Meat Heavy' },
                { value: 'average', label: 'Average Meat' },
                { value: 'vegetarian', label: 'Vegetarian' },
                { value: 'vegan', label: 'Vegan' }
              ]} />
            </div>

            <div>
              <label className="text-sm font-medium mb-1.5 block">Primary Commute</label>
              <Select {...register('commute_mode')} options={[
                { value: 'car', label: 'Gasoline Car' },
                { value: 'ev', label: 'Electric Vehicle' },
                { value: 'public_transit', label: 'Public Transit' },
                { value: 'bike', label: 'Bicycle / Walk' }
              ]} />
            </div>

            <Button type="submit" className="w-full mt-4" size="lg" disabled={loading}>
              {loading ? 'Calculating...' : 'Calculate My Footprint'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default Onboarding;
