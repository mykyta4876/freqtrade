<script setup lang="ts">
import { ref, computed } from 'vue';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Select from 'primevue/select';
import Card from 'primevue/card';
import ProgressSpinner from 'primevue/progressspinner';
import Message from 'primevue/message';

const botStore = useBotStore();
const loginInfo = useLoginInfo(botStore.selectedBot);
const { api } = useApi(loginInfo, botStore.selectedBot);

const pair = ref('BTC/USDT');
const timeframe = ref('5m');
const timerange = ref('');
const loading = ref(false);
const error = ref<string | null>(null);
const result = ref<any>(null);

const timeframes = [
  { label: '1m', value: '1m' },
  { label: '5m', value: '5m' },
  { label: '15m', value: '15m' },
  { label: '1h', value: '1h' },
  { label: '4h', value: '4h' },
  { label: '1d', value: '1d' },
];

const statusClass = computed(() => {
  if (!result.value) return '';
  const status = result.value.status;
  if (status === 'complete') return 'text-green-500';
  if (status === 'incomplete') return 'text-yellow-500';
  if (status === 'empty' || status === 'missing') return 'text-red-500';
  return '';
});

async function checkData() {
  if (!pair.value.trim()) {
    error.value = 'Please enter a trading pair';
    return;
  }

  loading.value = true;
  error.value = null;
  result.value = null;

  try {
    const params: any = {
      pair: pair.value.trim(),
      timeframe: timeframe.value,
    };

    if (timerange.value.trim()) {
      params.timerange = timerange.value.trim();
    }

    const response = await api.get('/api/v1/check_data', { params });
    result.value = response.data;
  } catch (err: any) {
    console.error('Error checking data:', err);
    error.value = err.response?.data?.detail || err.message || 'Failed to check data';
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="check-data-view p-4">
    <Card>
      <template #title>
        <div class="flex items-center gap-2">
          <i-mdi-database-search class="text-2xl" />
          <span>Check Data</span>
        </div>
      </template>
      <template #content>
        <div class="flex flex-col gap-4">
          <!-- Form -->
          <div class="flex flex-col md:flex-row gap-4">
            <div class="flex-1">
              <label class="block mb-2 text-sm font-medium">Trading Pair</label>
              <InputText v-model="pair" placeholder="BTC/USDT" class="w-full" />
            </div>
            <div class="flex-1">
              <label class="block mb-2 text-sm font-medium">Timeframe</label>
              <Select v-model="timeframe" :options="timeframes" optionLabel="label" optionValue="value" class="w-full" />
            </div>
            <div class="flex-1">
              <label class="block mb-2 text-sm font-medium">Timerange (optional)</label>
              <InputText v-model="timerange" placeholder="20260201-20260301" class="w-full" />
            </div>
            <div class="flex items-end">
              <Button label="Check Data" icon="i-mdi-magnify" @click="checkData" :loading="loading" />
            </div>
          </div>

          <!-- Error Message -->
          <Message v-if="error" severity="error" :closable="false">
            {{ error }}
          </Message>

          <!-- Loading -->
          <div v-if="loading" class="flex justify-center py-8">
            <ProgressSpinner />
          </div>

          <!-- Results -->
          <div v-if="result && !loading" class="mt-4">
            <Card>
              <template #title>
                <div class="flex items-center gap-2">
                  <span :class="statusClass" class="font-bold uppercase">{{ result.status }}</span>
                  <span class="text-sm font-normal">- {{ result.completeness_percent }}% Complete</span>
                </div>
              </template>
              <template #content>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div class="p-3 bg-surface-100 rounded">
                    <div class="text-sm text-surface-600">Total Candles</div>
                    <div class="text-2xl font-bold">{{ result.total_candles.toLocaleString() }}</div>
                  </div>
                  <div class="p-3 bg-surface-100 rounded">
                    <div class="text-sm text-surface-600">Expected Candles</div>
                    <div class="text-2xl font-bold">{{ result.expected_candles ? result.expected_candles.toLocaleString() : 'N/A' }}</div>
                  </div>
                  <div class="p-3 bg-surface-100 rounded">
                    <div class="text-sm text-surface-600">Missing Candles</div>
                    <div class="text-2xl font-bold text-yellow-600">{{ result.missing_candles.toLocaleString() }}</div>
                  </div>
                  <div class="p-3 bg-surface-100 rounded">
                    <div class="text-sm text-surface-600">Zero Volume</div>
                    <div class="text-2xl font-bold text-orange-600">{{ result.zero_volume_candles.toLocaleString() }}</div>
                  </div>
                </div>

                <div class="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <div class="text-sm text-surface-600">Data Start</div>
                    <div class="font-medium">{{ result.data_start || 'N/A' }}</div>
                  </div>
                  <div>
                    <div class="text-sm text-surface-600">Data End</div>
                    <div class="font-medium">{{ result.data_end || 'N/A' }}</div>
                  </div>
                </div>

                <!-- Gaps -->
                <div v-if="result.gaps && result.gaps.length > 0" class="mt-6">
                  <div class="text-lg font-semibold mb-3 text-yellow-600">⚠️ Data Gaps Found</div>
                  <div class="space-y-2">
                    <Card v-for="(gap, index) in result.gaps" :key="index" class="bg-yellow-50 dark:bg-yellow-900/20">
                      <template #content>
                        <div class="p-3">
                          <div class="font-semibold mb-2">Gap {{ index + 1 }}</div>
                          <div class="text-sm">
                            <div><strong>From:</strong> {{ gap.start }}</div>
                            <div><strong>To:</strong> {{ gap.end }}</div>
                            <div><strong>Missing Candles:</strong> {{ gap.missing_candles }}</div>
                          </div>
                        </div>
                      </template>
                    </Card>
                  </div>
                </div>
              </template>
            </Card>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<style scoped>
.check-data-view {
  max-width: 1400px;
  margin: 0 auto;
}
</style>
