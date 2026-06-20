import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageHeader } from '../../../components/layout/PageHeader';
import { Card, CardHeader } from '../../../components/ui/Card';
import { Button } from '../../../components/ui/Button';
import { StatusBadge } from '../../../components/ui/StatusBadge';
import { TrustScoreBadge } from '../../../components/ui/TrustScoreBadge';
import { FraudScoreBar } from '../../../components/ui/FraudScoreBar';
import { Spinner } from '../../../components/ui/Spinner';
import { Modal } from '../../../components/ui/Modal';
import { useClaim, useFraudReport, useClaimDecision } from '../../../hooks/useClaims';
import { formatDate, formatCurrency } from '../../../utils/format';
import {
  CheckCircleIcon,
  XCircleIcon,
  MagnifyingGlassIcon,
  ArrowLeftIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';

export function ClaimDetailPage() {
  const { claimId }                     = useParams<{ claimId: string }>();
  const navigate                        = useNavigate();
  const { data: claim, isLoading }      = useClaim(claimId!);
  const { data: fraud, isLoading: fl }  = useFraudReport(claimId!);
  const decisionMutation                = useClaimDecision(claimId!);
  const [showDecisionModal, setShow]    = useState(false);
  const [decisionType, setDecisionType] = useState <
    'approved' | 'rejected' | 'needs_inspection'
  >('approved');
  const [notes, setNotes]               = useState('');

  if (isLoading) {
    return (
      <div className="flex justify-center py-20">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!claim) {
    return (
      <div className="text-center py-20 text-ink-secondary">
        Claim not found.
      </div>
    );
  }

  const handleDecision = async () => {
    await decisionMutation.mutateAsync({
      status: decisionType,
      officer_notes: notes || undefined,
    });
    setShow(false);
    navigate('/officer/claims');
  };

  const openDecision = (type: typeof decisionType) => {
    setDecisionType(type);
    setNotes('');
    setShow(true);
  };

  const trustGrade =
    claim.trust_score !== null
      ? claim.trust_score >= 80 ? 'A'
      : claim.trust_score >= 60 ? 'B'
      : claim.trust_score >= 40 ? 'C'
      : claim.trust_score >= 20 ? 'D' : 'F'
      : null;

  const canDecide = !['approved', 'rejected'].includes(claim.status);

  return (
    <div>
      <PageHeader
        title="Claim Detail"
        subtitle={`ID: ${claimId?.slice(0, 8)}...`}
        action={
          <Button
            variant="ghost"
            onClick={() => navigate('/officer/claims')}
            leftIcon={<ArrowLeftIcon className="h-4 w-4" />}
            fullWidth={false}
          >
            Back
          </Button>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">

        {/* Left column — claim info + decision */}
        <div className="lg:col-span-1 space-y-5">

          {/* Claim Summary */}
          <Card>
            <CardHeader title="Claim Summary" />
            <div className="space-y-3 text-sm">
              <Row label="Status">
                <StatusBadge status={claim.status} />
              </Row>
              <Row label="Damage Type">
                <span className="capitalize">{claim.damage_type}</span>
              </Row>
              {claim.estimated_loss && (
                <Row label="Estimated Loss">
                  {formatCurrency(claim.estimated_loss)}
                </Row>
              )}
              {claim.affected_acres && (
                <Row label="Affected Area">
                  {claim.affected_acres} acres
                </Row>
              )}
              {claim.damage_description && (
                <div>
                  <p className="label mb-1">Description</p>
                  <p className="text-ink text-sm">{claim.damage_description}</p>
                </div>
              )}
              {claim.submitted_at && (
                <Row label="Submitted">
                  {formatDate(claim.submitted_at)}
                </Row>
              )}
              {claim.officer_notes && (
                <div>
                  <p className="label mb-1">Officer Notes</p>
                  <p className="text-ink text-sm italic">"{claim.officer_notes}"</p>
                </div>
              )}
            </div>
          </Card>

          {/* Trust Score */}
          <Card>
            <CardHeader title="Trust Score" />
            <div className="flex items-center gap-4">
              <TrustScoreBadge
                score={claim.trust_score}
                grade={trustGrade}
                size="lg"
              />
              <div className="text-sm text-ink-secondary">
                {trustGrade === 'A' && 'Highly trusted — recommend approval'}
                {trustGrade === 'B' && 'Trusted — standard processing'}
                {trustGrade === 'C' && 'Moderate — review recommended'}
                {trustGrade === 'D' && 'Low trust — inspection required'}
                {trustGrade === 'F' && 'Very low trust — likely fraud'}
                {!trustGrade && 'Fraud analysis pending...'}
              </div>
            </div>
          </Card>

          {/* Decision Buttons */}
          {canDecide && (
            <Card>
              <CardHeader title="Make Decision" />
              <div className="space-y-2">
                <Button
                  variant="primary"
                  fullWidth
                  leftIcon={<CheckCircleIcon className="h-4 w-4" />}
                  onClick={() => openDecision('approved')}
                >
                  Approve Claim
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  leftIcon={<MagnifyingGlassIcon className="h-4 w-4" />}
                  onClick={() => openDecision('needs_inspection')}
                >
                  Needs Inspection
                </Button>
                <Button
                  variant="danger"
                  fullWidth
                  leftIcon={<XCircleIcon className="h-4 w-4" />}
                  onClick={() => openDecision('rejected')}
                >
                  Reject Claim
                </Button>
              </div>
            </Card>
          )}
        </div>

        {/* Right column — fraud analysis */}
        <div className="lg:col-span-2 space-y-5">

          {/* Fraud Score Breakdown */}
          <Card>
            <CardHeader
              title="Fraud Analysis"
              subtitle={
                fraud?.status === 'analyzed'
                  ? `Generated ${fraud.generated_at ? formatDate(fraud.generated_at) : ''}`
                  : 'Analysis pending...'
              }
            />

            {fl ? (
              <div className="flex justify-center py-8">
                <Spinner />
              </div>
            ) : fraud?.status === 'not_analyzed' ? (
              <div className="text-center py-8 text-ink-secondary text-sm">
                Fraud analysis has not run yet for this claim.
              </div>
            ) : fraud ? (
              <div className="space-y-5">
                {/* Recommendation banner */}
                <div className={`rounded-xl p-4 flex items-center gap-3
                  ${fraud.recommendation === 'approve'
                    ? 'bg-green-50 border border-green-200'
                    : fraud.recommendation === 'reject'
                    ? 'bg-red-50 border border-red-200'
                    : 'bg-amber-50 border border-amber-200'
                  }`}>
                  <ExclamationTriangleIcon className={`h-5 w-5 flex-shrink-0
                    ${fraud.recommendation === 'approve' ? 'text-success'
                    : fraud.recommendation === 'reject' ? 'text-danger'
                    : 'text-warning'}`}
                  />
                  <div>
                    <p className="font-medium text-sm">
                      AI Recommendation:{' '}
                      <span className="capitalize font-bold">
                        {fraud.recommendation?.replace('_', ' ')}
                      </span>
                    </p>
                    <p className="text-xs text-ink-secondary mt-0.5">
                      Trust: {fraud.trust_score?.toFixed(1)} | Fraud Risk: {fraud.fraud_score?.toFixed(1)}
                    </p>
                  </div>
                </div>

                {/* Signal bars */}
                <div className="space-y-4">
                  <FraudScoreBar
                    label="GPS Consistency"
                    score={fraud.gps_score}
                    maxScore={25}
                    flags={(fraud.flags ?? []).filter(f => f.includes('GPS'))}
                  />
                  <FraudScoreBar
                    label="Lifecycle Completeness"
                    score={fraud.lifecycle_score}
                    maxScore={25}
                    flags={(fraud.flags ?? []).filter(f =>
                      f.includes('STAGE') || f.includes('LIFECYCLE') || f.includes('UPLOAD')
                    )}
                  />
                  <FraudScoreBar
                    label="Image Originality"
                    score={fraud.hash_score}
                    maxScore={20}
                    flags={(fraud.flags ?? []).filter(f => f.includes('DUPLICATE') || f.includes('REPEATED'))}
                  />
                  <FraudScoreBar
                    label="Weather Validation"
                    score={fraud.weather_score}
                    maxScore={20}
                    flags={(fraud.flags ?? []).filter(f => f.includes('WEATHER'))}
                  />
                  <FraudScoreBar
                    label="Document Validity"
                    score={fraud.document_score}
                    maxScore={10}
                    flags={(fraud.flags ?? []).filter(f =>
                      f.includes('MISSING') || f.includes('INVALID') || f.includes('DOCUMENT')
                    )}
                  />
                </div>

                {/* All flags */}
                {fraud.flags && fraud.flags.length > 0 && (
                  <div>
                    <p className="label mb-2">All Flags ({fraud.flags.length})</p>
                    <div className="space-y-1.5">
                      {fraud.flags.map((flag, i) => (
                        <div
                          key={i}
                          className="flex items-start gap-2 text-xs bg-red-50
                                     border border-red-100 rounded-lg px-3 py-2"
                        >
                          <span className="text-danger mt-0.5">⚠</span>
                          <span className="text-red-800">{flag}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : null}
          </Card>
        </div>
      </div>

      {/* Decision Modal */}
      <Modal
        isOpen={showDecisionModal}
        onClose={() => setShow(false)}
        title={`${
          decisionType === 'approved' ? 'Approve'
          : decisionType === 'rejected' ? 'Reject'
          : 'Flag for Inspection'
        } Claim`}
        size="md"
      >
        <div className="space-y-4">
          <p className="text-sm text-ink-secondary">
            {decisionType === 'approved'
              ? 'This will approve the claim and notify the farmer.'
              : decisionType === 'rejected'
              ? 'This will reject the claim. Please provide a reason.'
              : 'This will flag the claim for physical inspection.'}
          </p>
          <div>
            <label className="label mb-1 block">
              Officer Notes {decisionType === 'rejected' ? '(required)' : '(optional)'}
            </label>
            <textarea
              value={notes}
              onChange={e => setNotes(e.target.value)}
              rows={3}
              className="w-full rounded-lg border border-border bg-surface px-3 py-2
                         text-sm focus:outline-none focus:ring-2 focus:ring-primary-700"
              placeholder="Add notes for the farmer or for records..."
            />
          </div>
          <div className="flex gap-3">
            <Button
              variant={
                decisionType === 'approved' ? 'primary'
                : decisionType === 'rejected' ? 'danger'
                : 'secondary'
              }
              fullWidth
              isLoading={decisionMutation.isPending}
              onClick={handleDecision}
            >
              Confirm
            </Button>
            <Button
              variant="ghost"
              fullWidth
              onClick={() => setShow(false)}
            >
              Cancel
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

function Row({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex items-center justify-between">
      <span className="label">{label}</span>
      <span className="value font-medium">{children}</span>
    </div>
  );
}