/**
 * Main JavaScript for RailSewa Dashboard
 */

let currentFilter = 'all';
let responseModal;

$(document).ready(function() {
    // Initialize Bootstrap modal
    responseModal = new bootstrap.Modal(document.getElementById('responseModal'));
    
    // Character counter for response textarea
    $('#response-text').on('input', function() {
        const length = $(this).val().length;
        $('#char-count').text(length);
        
        if (length > 500) {
            $('#char-count').css('color', '#dc3545');
        } else {
            $('#char-count').css('color', '#6c757d');
        }
    });
    
    // Load initial data
    loadStats();
    loadTweets();
    
    // Auto-refresh every 30 seconds
    setInterval(function() {
        loadStats();
        loadTweets();
    }, 30000);
});

function loadStats() {
    $.ajax({
        url: 'index.php',
        method: 'POST',
        data: {
            action: 'get_stats'
        },
        dataType: 'json',
        success: function(data) {
            $('#stat-total').text(data.total || 0);
            $('#stat-emergency').text(data.emergency || 0);
            $('#stat-feedback').text(data.feedback || 0);
            $('#stat-responded').text(data.responded || 0);
        },
        error: function(xhr, status, error) {
            console.error('Error loading stats:', error);
        }
    });
}

function loadTweets() {
    $.ajax({
        url: 'index.php',
        method: 'POST',
        data: {
            action: 'get_tweets',
            filter: currentFilter
        },
        dataType: 'json',
        success: function(data) {
            displayTweets(data);
        },
        error: function(xhr, status, error) {
            console.error('Error loading tweets:', error);
            $('#tweets-tbody').html('<tr><td colspan="8" class="text-center text-danger">Error loading complaints</td></tr>');
        }
    });
}

function displayTweets(tweets) {
    const tbody = $('#tweets-tbody');
    
    if (tweets.length === 0) {
        tbody.html('<tr><td colspan="8" class="text-center">No complaints found</td></tr>');
        return;
    }
    
    let html = '';
    
        tweets.forEach(function(complaint) {
            const typeBadge = complaint.prediction == 1 
                ? '<span class="badge-emergency">Emergency</span>'
                : '<span class="badge-feedback">Feedback</span>';
            
            const statusBadge = complaint.response_status == 1
                ? '<span class="badge-responded">Responded</span>'
                : '<span class="badge-pending">Pending</span>';
            
            const pnr = complaint.pnr ? complaint.pnr : '-';
            const time = new Date(complaint.time).toLocaleString();
            const source = complaint.source || 'Telegram';
            
            html += `
                <tr>
                    <td>${complaint.id}</td>
                    <td class="tweet-text">${escapeHtml(complaint.tweet)}</td>
                    <td>${escapeHtml(complaint.username || 'Unknown')} <small class="text-muted">(${source})</small></td>
                    <td>${pnr}</td>
                    <td>${typeBadge}</td>
                    <td>${time}</td>
                    <td>${statusBadge}</td>
                    <td>
                        ${complaint.response_status == 0 
                            ? `<button class="btn btn-sm btn-primary btn-action" onclick="openResponseModal(${complaint.id}, '${escapeHtml(complaint.tweet)}')">
                                <i class="fas fa-reply"></i> Respond
                               </button>`
                            : `<span class="text-muted">${escapeHtml(complaint.response || 'No response')}</span>`
                        }
                    </td>
                </tr>
            `;
        });
    
    tbody.html(html);
}

function filterTweets(filter) {
    currentFilter = filter;
    
    // Update button states
    $('.btn-group button').removeClass('active');
    
    if (filter === 'all') {
        $('.btn-group button:first').addClass('active');
    } else if (filter === 'emergency') {
        $('.btn-group button:nth-child(2)').addClass('active');
    } else if (filter === 'feedback') {
        $('.btn-group button:last').addClass('active');
    }
    
    loadTweets();
}

function openResponseModal(tweetId, tweetText) {
    $('#modal-tweet-id').val(tweetId);
    $('#modal-tweet-text').text(tweetText);
    $('#response-text').val('');
    $('#char-count').text('0');
    responseModal.show();
}

function submitResponse() {
    const tweetId = $('#modal-tweet-id').val();
    const response = $('#response-text').val();
    
    if (!response.trim()) {
        alert('Please enter a response');
        return;
    }
    
    if (response.length > 500) {
        alert('Response cannot exceed 500 characters');
        return;
    }
    
    $.ajax({
        url: 'index.php',
        method: 'POST',
        data: {
            action: 'respond_tweet',
            tweet_id: tweetId,
            response: response
        },
        dataType: 'json',
        success: function(data) {
            if (data.status === 'success') {
                responseModal.hide();
                loadTweets();
                loadStats();
                alert('Response sent successfully!');
            } else {
                alert('Error: ' + data.message);
            }
        },
        error: function(xhr, status, error) {
            alert('Error sending response: ' + error);
        }
    });
}

function refreshData() {
    loadStats();
    loadTweets();
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text ? text.replace(/[&<>"']/g, m => map[m]) : '';
}

