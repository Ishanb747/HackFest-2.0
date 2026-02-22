import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, ScanLine, ArrowRight, Shield } from 'lucide-react';
import { useScan } from '../../context/ScanContext';
import Button from './Button';
import './GateGuard.css';

/**
 * Wraps any page that requires a completed scan.
 * If no data exists yet, renders a full-page lock screen.
 */
function GateGuard({ children }) {
    const { hasData, loading } = useScan();
    const navigate = useNavigate();

    if (loading) {
        return (
            <div className="gate-loading">
                <div className="gate-spinner" />
            </div>
        );
    }

    if (!hasData) {
        return (
            <div className="gate-page">
                <div className="gate-card">
                    <div className="gate-icon-wrap">
                        <Lock size={40} />
                    </div>

                    <h1 className="gate-title">Scan Required</h1>
                    <p className="gate-subtitle">
                        No policy data found yet. Upload a regulatory PDF and run the pipeline
                        to unlock this section.
                    </p>

                    <div className="gate-steps">
                        <div className="gate-step">
                            <div className="step-num">1</div>
                            <span>Upload your regulatory policy PDF</span>
                        </div>
                        <div className="gate-step">
                            <div className="step-num">2</div>
                            <span>Choose a scan phase (Full Scan recommended)</span>
                        </div>
                        <div className="gate-step">
                            <div className="step-num">3</div>
                            <span>Wait for the pipeline to complete</span>
                        </div>
                        <div className="gate-step">
                            <div className="step-num">4</div>
                            <span>All pages unlock automatically ✓</span>
                        </div>
                    </div>

                    <Button
                        variant="primary"
                        size="lg"
                        icon={ScanLine}
                        onClick={() => navigate('/scan-now')}
                    >
                        Go to Scan Now
                        <ArrowRight size={16} />
                    </Button>
                </div>
            </div>
        );
    }

    return children;
}

export default GateGuard;
