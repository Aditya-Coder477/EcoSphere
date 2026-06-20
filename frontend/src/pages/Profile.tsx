import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useAppStore } from '../store/useAppStore';
import { mockUserProfile } from '../mocks';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { Button } from '../components/ui/Button';
import { CheckCircle2, User, MapPin, Home, Zap, ShoppingCart } from 'lucide-react';

const schema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email').optional().or(z.literal('')),
  occupation: z.string().optional(),
  country: z.string().min(1, 'Country is required'),
  household_size: z.coerce.number().min(1).max(20),
  diet: z.string().min(1),
  commute_mode: z.string().min(1),
  budget_level: z.string().min(1),
  electricity_source: z.string().optional(),
  electricity_kwh_per_year: z.coerce.number().min(0).optional(),
});

type FormValues = z.infer<typeof schema>;

const SectionTitle: React.FC<{ icon: React.ReactNode; title: string }> = ({ icon, title }) => (
  <div className="flex items-center gap-2 mb-4 pb-2 border-b border-border">
    <span className="text-primary">{icon}</span>
    <h2 className="text-sm font-semibold text-text-muted uppercase tracking-wider">{title}</h2>
  </div>
);

const Profile = () => {
  const { user, setUser } = useAppStore();
  const [saved, setSaved] = useState(false);
  const isDemo = !user;

  const activeProfile = user ?? mockUserProfile;

  const { register, handleSubmit, reset, formState: { errors, isDirty } } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: activeProfile.name,
      email: activeProfile.email ?? '',
      occupation: activeProfile.occupation ?? '',
      country: activeProfile.preferences.country,
      household_size: activeProfile.preferences.household_size,
      diet: activeProfile.preferences.diet,
      commute_mode: activeProfile.preferences.commute_mode,
      budget_level: activeProfile.preferences.budget_level,
      electricity_source: activeProfile.preferences.electricity_source ?? 'grid',
      electricity_kwh_per_year: activeProfile.preferences.electricity_kwh_per_year ?? 4200,
    },
  });

  const onSubmit = (data: FormValues) => {
    const updated = {
      id: activeProfile.id,
      name: data.name,
      email: data.email,
      occupation: data.occupation,
      preferences: {
        country: data.country,
        household_size: data.household_size,
        diet: data.diet,
        commute_mode: data.commute_mode,
        budget_level: data.budget_level,
        electricity_source: data.electricity_source,
        electricity_kwh_per_year: data.electricity_kwh_per_year,
      },
    };
    setUser(updated);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleReset = () => {
    reset();
    setSaved(false);
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Your Profile</h1>
        <p className="text-text-muted mt-1">Manage your lifestyle preferences and carbon profile.</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6" noValidate>

        {/* Identity section */}
        <Card>
          <CardContent className="p-6">
            <SectionTitle icon={<User className="w-4 h-4" />} title="Identity" />
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label className="text-sm font-medium mb-1.5 block">Full Name</label>
                <Input {...register('name')} placeholder="Your name" />
                {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name.message}</p>}
              </div>
              <div>
                <label className="text-sm font-medium mb-1.5 block">Email</label>
                <Input {...register('email')} type="email" placeholder="your@email.com" />
                {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email.message}</p>}
              </div>
              <div className="sm:col-span-2">
                <label className="text-sm font-medium mb-1.5 block">Occupation</label>
                <Input {...register('occupation')} placeholder="e.g. Software Engineer, Student" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Location & Household */}
        <Card>
          <CardContent className="p-6">
            <SectionTitle icon={<MapPin className="w-4 h-4" />} title="Location & Household" />
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label className="text-sm font-medium mb-1.5 block">Country</label>
                <Select
                  {...register('country')}
                  options={[
                    { value: 'IND', label: 'India' },
                    { value: 'USA', label: 'United States' },
                    { value: 'GBR', label: 'United Kingdom' },
                    { value: 'DEU', label: 'Germany' },
                    { value: 'AUS', label: 'Australia' },
                    { value: 'CHN', label: 'China' },
                  ]}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1.5 block">Household Size</label>
                <Input type="number" {...register('household_size')} min={1} max={20} />
                {errors.household_size && <p className="text-red-500 text-xs mt-1">{errors.household_size.message}</p>}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Lifestyle */}
        <Card>
          <CardContent className="p-6">
            <SectionTitle icon={<Home className="w-4 h-4" />} title="Lifestyle" />
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label className="text-sm font-medium mb-1.5 block">Diet Pattern</label>
                <Select
                  {...register('diet')}
                  options={[
                    { value: 'meat_heavy', label: 'Meat Heavy' },
                    { value: 'average', label: 'Average (some meat)' },
                    { value: 'vegetarian', label: 'Vegetarian' },
                    { value: 'vegan', label: 'Vegan' },
                  ]}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1.5 block">Primary Commute</label>
                <Select
                  {...register('commute_mode')}
                  options={[
                    { value: 'car', label: 'Gasoline Car' },
                    { value: 'ev', label: 'Electric Vehicle' },
                    { value: 'public_transit', label: 'Public Transit' },
                    { value: 'bike', label: 'Bicycle / Walk' },
                    { value: 'motorbike', label: 'Motorbike' },
                  ]}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1.5 block">Budget Level</label>
                <Select
                  {...register('budget_level')}
                  options={[
                    { value: 'low', label: 'Low (student / tight)' },
                    { value: 'medium', label: 'Medium' },
                    { value: 'high', label: 'High' },
                  ]}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Energy */}
        <Card>
          <CardContent className="p-6">
            <SectionTitle icon={<Zap className="w-4 h-4" />} title="Energy Usage" />
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label className="text-sm font-medium mb-1.5 block">Electricity Source</label>
                <Select
                  {...register('electricity_source')}
                  options={[
                    { value: 'grid', label: 'National Grid' },
                    { value: 'solar', label: 'Solar / Renewable' },
                    { value: 'mixed', label: 'Mixed (grid + solar)' },
                    { value: 'unknown', label: 'Not sure' },
                  ]}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-1.5 block">Annual Usage (kWh)</label>
                <Input type="number" {...register('electricity_kwh_per_year')} placeholder="e.g. 4200" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Action buttons */}
        <div className="flex items-center gap-3">
          <Button type="submit" disabled={!isDirty && !isDemo} className="px-8">
            Save Profile
          </Button>
          <Button type="button" variant="outline" onClick={handleReset} disabled={!isDirty}>
            Reset
          </Button>
          {saved && (
            <span className="flex items-center gap-1.5 text-sm text-emerald-400 font-medium">
              <CheckCircle2 className="w-4 h-4" aria-hidden="true" />
              Saved!
            </span>
          )}
        </div>
      </form>
    </div>
  );
};

export default Profile;
