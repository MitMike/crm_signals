frappe.ui.form.on('CRM Signal', {
    refresh: function(frm) {
        if (!frm.doc.is_read) {
            frm.add_custom_button(__('Mark as Read'), function() {
                frm.set_value('is_read', 1);
                frm.save();
            }).addClass('btn-primary');
        }
    }
});
