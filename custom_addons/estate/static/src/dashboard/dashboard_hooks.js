/** @odoo-module **/

import { useState } from "@odoo/owl";

/**
 * Dashboard yapılandırmasını (aktif/pasif öğeler) yöneten ve 
 * sunucu tarafında saklayan özel hook.
 */
export function useDashboardConfig(items, rpc) {
    const allItemIds = items.map(item => item.id);
    
    const state = useState({
        enabledItems: [...allItemIds],
        isLoaded: false,
    });

    // Sunucudan ayarları yükle
    async function loadSettings() {
        try {
            const savedItems = await rpc("/estate/dashboard/settings/get");
            if (savedItems && savedItems.length > 0) {
                state.enabledItems = savedItems;
            }
        } catch (error) {
            console.error("Failed to load dashboard settings:", error);
        } finally {
            state.isLoaded = true;
        }
    }

    // İlk yüklemeyi başlat
    const initialLoad = loadSettings();

    return {
        get enabledItems() {
            return state.enabledItems;
        },
        get isLoaded() {
            return state.isLoaded;
        },
        initialLoad,
        async update(newEnabledItems) {
            state.enabledItems = newEnabledItems;
            try {
                await rpc("/estate/dashboard/settings/set", {
                    enabled_items: newEnabledItems
                });
            } catch (error) {
                console.error("Failed to save dashboard settings:", error);
            }
        }
    };
}
