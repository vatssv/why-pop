import React from "react";
import "../spinner.css";

export default function LoadingSpinner() {
    return (
        <React.Fragment>
            <div className="spinner-container">
                <div className="loading-spinner">
                </div>
            </div>
        </React.Fragment>
    )
}