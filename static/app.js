

// --- RESIDENT DASHBOARD RENDERING FUNCTIONS ---

function renderResidentPaymentsDashboard(payments) {
    const container = document.getElementById('panel-container');
    
    let unpaid = payments.filter(p => p.status === 'Unpaid');
    let paid = payments.filter(p => p.status === 'Paid');
    
    // Calculate total unpaid and paid this month
    const totalUnpaid = unpaid.reduce((sum, p) => sum + (parseFloat(p.amount_due) || 0), 0).toFixed(2);
    
    const currMonth = new Date().toLocaleString('default', { month: 'long', year: 'numeric' });
    const paidThisMonth = paid.filter(p => {
        if (!p.payment_date) return false;
        const d = new Date(p.payment_date);
        return d.getMonth() === new Date().getMonth() && d.getFullYear() === new Date().getFullYear();
    }).reduce((sum, p) => sum + (parseFloat(p.amount_due) || 0), 0).toFixed(2);
    
    let html = `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
            <div class="glass-card" style="padding: 1.5rem; border-left: 4px solid #ef4444; display: flex; flex-direction: column; justify-content: center;">
                <div style="color: #a1a1aa; font-size: 0.9rem; margin-bottom: 0.5rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;">Total Outstanding</div>
                <div style="font-size: 2rem; font-weight: 700; color: #fca5a5;">₹${totalUnpaid}</div>
            </div>
            <div class="glass-card" style="padding: 1.5rem; border-left: 4px solid #10b981; display: flex; flex-direction: column; justify-content: center;">
                <div style="color: #a1a1aa; font-size: 0.9rem; margin-bottom: 0.5rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;">Paid This Month</div>
                <div style="font-size: 2rem; font-weight: 700; color: #6ee7b7;">₹${paidThisMonth}</div>
            </div>
        </div>
        
        <h3 style="margin-bottom: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 0.5rem;">Outstanding Payments</h3>
    `;
    
    if (unpaid.length === 0) {
        html += `<div class="glass-card" style="padding: 2rem; text-align: center; color: #a1a1aa; margin-bottom: 2rem;">No outstanding payments! You're all caught up.</div>`;
    } else {
        html += `<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; margin-bottom: 2rem;">`;
        unpaid.forEach(p => {
            let typeDesc = p.description || 'Monthly Rent';
            html += `
                <div class="glass-card" style="padding: 1.5rem; display: flex; flex-direction: column; position: relative; overflow: hidden;">
                    <div style="position: absolute; top: 0; right: 0; background: #ef4444; color: white; padding: 0.25rem 0.75rem; font-size: 0.75rem; font-weight: bold; border-bottom-left-radius: 8px;">UNPAID</div>
                    <div style="color: #a1a1aa; font-size: 0.85rem; margin-bottom: 0.25rem;">${p.billing_month}</div>
                    <div style="font-weight: 600; font-size: 1.1rem; margin-bottom: 1rem; color: #fff;">${typeDesc}</div>
                    <div style="font-size: 1.75rem; font-weight: 700; color: #fca5a5; margin-bottom: 1.5rem;">₹${parseFloat(p.amount_due).toFixed(2)}</div>
                    <button onclick="payFee('${p.payment_id}');" style="margin-top: auto; padding: 0.75rem; background: #10b981; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; transition: background 0.2s;" onmouseover="this.style.background='#059669'" onmouseout="this.style.background='#10b981'">Pay Now</button>
                </div>
            `;
        });
        html += `</div>`;
    }
    
    html += `<h3 style="margin-bottom: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 0.5rem;">Payment History</h3>`;
    
    if (paid.length === 0) {
        html += `<div class="glass-card" style="padding: 2rem; text-align: center; color: #a1a1aa;">No payment history available.</div>`;
    } else {
        html += `<div class="glass-card" style="overflow-x:auto;">
            <table style="width:100%; border-collapse: collapse; text-align: left; font-size: 0.95rem;">
                <thead>
                    <tr>
                        <th style="padding: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1); color: #e4e4e7;">Date</th>
                        <th style="padding: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1); color: #e4e4e7;">Description</th>
                        <th style="padding: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1); color: #e4e4e7;">Month</th>
                        <th style="padding: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1); color: #e4e4e7;">Amount</th>
                        <th style="padding: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1); color: #e4e4e7;">Method</th>
                        <th style="padding: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1); color: #e4e4e7;">Status</th>
                        <th style="padding: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1); color: #e4e4e7;">Action</th>
                    </tr>
                </thead>
                <tbody>
        `;
        // Sort paid by date descending
        paid.sort((a,b) => new Date(b.payment_date) - new Date(a.payment_date));
        
        paid.forEach(p => {
            const dateStr = p.payment_date ? new Date(p.payment_date).toLocaleDateString('en-GB', {day: '2-digit', month: 'short', year: 'numeric'}) : '-';
            html += `
                <tr style="transition: background 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.05)'" onmouseout="this.style.background='transparent'">
                    <td style="padding: 1rem; border-bottom: 1px solid rgba(255,255,255,0.05); color: #d4d4d8;">${dateStr}</td>
                    <td style="padding: 1rem; border-bottom: 1px solid rgba(255,255,255,0.05); color: #d4d4d8;">${p.description || 'Monthly Rent'}</td>
                    <td style="padding: 1rem; border-bottom: 1px solid rgba(255,255,255,0.05); color: #d4d4d8;">${p.billing_month}</td>
                    <td style="padding: 1rem; border-bottom: 1px solid rgba(255,255,255,0.05); color: #d4d4d8; font-weight: 500;">₹${parseFloat(p.amount_due).toFixed(2)}</td>
                    <td style="padding: 1rem; border-bottom: 1px solid rgba(255,255,255,0.05); color: #d4d4d8;">${p.payment_method || '-'}</td>
                    <td style="padding: 1rem; border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <span style="background: rgba(16, 185, 129, 0.15); color: #34d399; padding: 0.25rem 0.5rem; border-radius: 9999px; font-size: 0.8rem; font-weight: 600; border: 1px solid rgba(16, 185, 129, 0.3);">PAID</span>
                    </td>
                    <td style="padding: 1rem; border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <button onclick="renderReceiptModal('${p.payment_id}')" style="background: transparent; color: #60a5fa; border: 1px solid #60a5fa; padding: 0.25rem 0.75rem; border-radius: 4px; cursor: pointer; font-size: 0.85rem; transition: all 0.2s;" onmouseover="this.style.background='#60a5fa'; this.style.color='#fff';" onmouseout="this.style.background='transparent'; this.style.color='#60a5fa';">View Receipt</button>
                    </td>
                </tr>
            `;
        });
        html += `</tbody></table></div>`;
    }

    container.innerHTML = html;
}

async function renderReceiptModal(paymentId) {
    try {
        const payment = await apiFetch(`payments/${paymentId}`);
        const fullName = localStorage.getItem('dwell_name') || 'Resident';
        const flatId = localStorage.getItem('dwell_flat_id') || '';
        
        let flatData = { block_name: 'Unknown' };
        try {
            flatData = await apiFetch(`flats/${flatId}`);
        } catch (e) { }

        const overlay = document.createElement('div');
        overlay.id = 'receipt-modal-overlay';
        overlay.style.cssText = `
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.7); z-index: 1000;
            display: flex; justify-content: center; align-items: center;
            backdrop-filter: blur(4px);
        `;
        
        const dateStr = payment.payment_date ? new Date(payment.payment_date).toLocaleDateString('en-GB', {day: '2-digit', month: 'long', year: 'numeric'}) : '-';
        
        const receiptHtml = `
            <div id="receipt-card" style="background: white; color: black; padding: 3rem; border-radius: 8px; width: 90%; max-width: 600px; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); position: relative;">
                <button onclick="document.getElementById('receipt-modal-overlay').remove()" style="position: absolute; top: 1rem; right: 1rem; background: transparent; border: none; font-size: 1.5rem; cursor: pointer; color: #a1a1aa;" class="no-print">&times;</button>
                
                <div style="text-align: center; border-bottom: 2px dashed #d4d4d8; padding-bottom: 1.5rem; margin-bottom: 2rem;">
                    <h2 style="margin: 0 0 0.5rem 0; color: #1f2937; letter-spacing: 1px;">DWELLMANAGER</h2>
                    <div style="color: #4b5563; font-weight: 600; font-size: 1.2rem;">Payment Receipt</div>
                </div>
                
                <div style="display: flex; justify-content: space-between; margin-bottom: 2rem; color: #3f3f46;">
                    <div>
                        <div style="margin-bottom: 0.5rem;"><strong>Receipt No:</strong> <span style="font-family: monospace;">${payment.receipt_ref || '-'}</span></div>
                        <div style="margin-bottom: 0.5rem;"><strong>Payment ID:</strong> <span style="font-family: monospace;">${payment.payment_id}</span></div>
                    </div>
                    <div style="text-align: right;">
                        <div style="margin-bottom: 0.5rem;"><strong>Date:</strong> ${dateStr}</div>
                        <div style="margin-bottom: 0.5rem;"><strong>Status:</strong> <span style="color: #10b981; font-weight: 800;">PAID</span></div>
                    </div>
                </div>
                
                <div style="background: #f4f4f5; padding: 1.5rem; border-radius: 6px; margin-bottom: 2rem;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                        <div>
                            <div style="color: #71717a; font-size: 0.85rem; text-transform: uppercase;">Resident Name</div>
                            <div style="font-weight: 600; color: #1f2937;">${fullName}</div>
                        </div>
                        <div>
                            <div style="color: #71717a; font-size: 0.85rem; text-transform: uppercase;">Flat Number</div>
                            <div style="font-weight: 600; color: #1f2937;">${flatData.block_name} - ${flatId}</div>
                        </div>
                        <div style="grid-column: span 2;">
                            <div style="color: #71717a; font-size: 0.85rem; text-transform: uppercase;">Payment Type</div>
                            <div style="font-weight: 600; color: #1f2937;">${payment.description || 'Monthly Rent'}</div>
                        </div>
                    </div>
                </div>
                
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 2rem;">
                    <tr style="border-bottom: 2px solid #e4e4e7;">
                        <th style="text-align: left; padding: 0.75rem 0; color: #3f3f46;">Description</th>
                        <th style="text-align: right; padding: 0.75rem 0; color: #3f3f46;">Amount</th>
                    </tr>
                    <tr style="border-bottom: 1px solid #e4e4e7;">
                        <td style="padding: 1rem 0; color: #1f2937;">Billing Month: ${payment.billing_month}</td>
                        <td style="text-align: right; padding: 1rem 0; font-weight: 600; color: #1f2937;">₹${parseFloat(payment.amount_due).toFixed(2)}</td>
                    </tr>
                    <tr>
                        <td style="padding: 1rem 0; font-weight: 700; font-size: 1.2rem; color: #1f2937;">Total Paid</td>
                        <td style="text-align: right; padding: 1rem 0; font-weight: 700; font-size: 1.2rem; color: #10b981;">₹${parseFloat(payment.amount_due).toFixed(2)}</td>
                    </tr>
                </table>
                
                <div style="text-align: center; color: #71717a; font-size: 0.9rem; margin-bottom: 2rem;">
                    Payment Method: <strong>${payment.payment_method || '-'}</strong>
                </div>
                
                <div class="no-print" style="text-align: center;">
                    <button onclick="window.print()" style="padding: 0.75rem 2rem; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 1rem; box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.5);">Print Receipt</button>
                </div>
            </div>
        `;
        
        overlay.innerHTML = receiptHtml;
        document.body.appendChild(overlay);
        
        // Add print styling if not present
        if (!document.getElementById('print-style')) {
            const style = document.createElement('style');
            style.id = 'print-style';
            style.innerHTML = `
                @media print {
                    body * { visibility: hidden; }
                    #receipt-card, #receipt-card * { visibility: visible; }
                    #receipt-card { position: absolute; left: 0; top: 0; width: 100%; box-shadow: none; padding: 0; }
                    .no-print { display: none !important; }
                    #receipt-modal-overlay { background: transparent; backdrop-filter: none; }
                }
            `;
            document.head.appendChild(style);
        }
        
    } catch (e) {
        alert("Failed to load receipt details.");
    }
}

function renderResidentComplaintsDashboard(complaints) {
    const container = document.getElementById('panel-container');
    
    let html = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
            <h2 style="margin: 0;">My Complaints</h2>
            <button onclick="loadView('request_maintenance')" style="padding: 0.6rem 1.2rem; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; transition: background 0.2s;" onmouseover="this.style.background='#2563eb'" onmouseout="this.style.background='#3b82f6'">+ New Complaint</button>
        </div>
    `;
    
    if (!complaints || complaints.length === 0) {
        html += `<div class="glass-card" style="padding: 3rem; text-align: center; color: #a1a1aa;">You have no maintenance complaints.</div>`;
    } else {
        html += `<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1.5rem;">`;
        
        // Sort newest first
        complaints.sort((a,b) => new Date(b.logged_at) - new Date(a.logged_at));
        
        complaints.forEach(c => {
            const dateStr = new Date(c.logged_at).toLocaleDateString('en-GB', {day: '2-digit', month: 'short', year: 'numeric'});
            
            let badgeBg, badgeColor;
            if (c.status === 'Pending') { badgeBg = 'rgba(245, 158, 11, 0.15)'; badgeColor = '#fcd34d'; }
            else if (c.status === 'Assigned') { badgeBg = 'rgba(59, 130, 246, 0.15)'; badgeColor = '#93c5fd'; }
            else if (c.status === 'Resolved') { badgeBg = 'rgba(16, 185, 129, 0.15)'; badgeColor = '#6ee7b7'; }
            
            html += `
                <div class="glass-card" style="padding: 1.5rem; display: flex; flex-direction: column;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                        <div>
                            <div style="color: #60a5fa; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">${c.category}</div>
                            <div style="font-weight: 600; font-size: 1.1rem; color: #fff;">${c.title}</div>
                        </div>
                        <span style="background: ${badgeBg}; color: ${badgeColor}; padding: 0.25rem 0.6rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; border: 1px solid ${badgeBg.replace('0.15', '0.3')};">${c.status}</span>
                    </div>
                    
                    <div style="color: #d4d4d8; font-size: 0.9rem; line-height: 1.5; margin-bottom: 1.5rem; flex-grow: 1;">${c.description}</div>
                    
                    <div style="background: rgba(0,0,0,0.2); padding: 1rem; border-radius: 6px; font-size: 0.85rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="color: #a1a1aa;">Complaint ID:</span>
                            <span style="font-family: monospace; color: #e4e4e7;">${c.complaint_id}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="color: #a1a1aa;">Submitted:</span>
                            <span style="color: #e4e4e7;">${dateStr}</span>
                        </div>
            `;
            
            if (c.status === 'Assigned' || c.assigned_to) {
                html += `
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; border-top: 1px dashed rgba(255,255,255,0.1); padding-top: 0.5rem; margin-top: 0.5rem;">
                            <span style="color: #a1a1aa;">Assigned To:</span>
                            <span style="color: #e4e4e7; font-weight: 500;">${c.assigned_to || '-'}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span style="color: #a1a1aa;">Scheduled:</span>
                            <span style="color: #e4e4e7;">${c.scheduled_date || '-'}</span>
                        </div>
                `;
            }
            
            html += `
                    </div>
                </div>
            `;
        });
        html += `</div>`;
    }
    
    container.innerHTML = html;
}
