<script setup lang="ts">
import { MarginMode, TradingMode } from '@/types';
import type { ExchangeSelection, Markets, MarketsPayload, PairHistoryPayload } from '@/types';

const botStore = useBotStore();
const chartStore = useChartConfigStore();

const finalTimeframe = computed<string>(() => {
  return botStore.activeBot.isWebserverMode
    ? chartStore.selectedTimeframe || botStore.activeBot.strategy.timeframe || ''
    : botStore.activeBot.timeframe;
});

const availablePairs = computed<string[]>(() => {
  if (botStore.activeBot.isWebserverMode) {
    return Object.keys(markets.value?.markets || {}).sort() || [];
  }
  return botStore.activeBot.whitelist;
});

onMounted(async () => {
  // Force live mode for this dedicated page.
  chartStore.useLiveData = true;

  if (botStore.activeBot.isWebserverMode) {
    const payload: MarketsPayload = {};
    if (exchange.value.customExchange) {
      payload.exchange = exchange.value.selectedExchange.exchange;
      payload.trading_mode = exchange.value.selectedExchange.trade_mode.trading_mode;
      payload.margin_mode = exchange.value.selectedExchange.trade_mode.margin_mode;
    }
    markets.value = await botStore.activeBot.getMarkets(payload);
  } else if (!botStore.activeBot.whitelist || botStore.activeBot.whitelist.length === 0) {
    botStore.activeBot.getWhitelist();
  }
});

function refreshOHLCV(pair: string, columns: string[]) {
  if (botStore.activeBot.isWebserverMode && finalTimeframe.value) {
    const payload: PairHistoryPayload = {
      pair,
      timeframe: finalTimeframe.value,
      timerange: chartStore.timerange || '',
      strategy: chartStore.strategy,
      columns,
      live_mode: true,
    };
    if (exchange.value.customExchange) {
      payload.exchange = exchange.value.selectedExchange.exchange;
      payload.trading_mode = exchange.value.selectedExchange.trade_mode.trading_mode;
      payload.margin_mode = exchange.value.selectedExchange.trade_mode.margin_mode;
    }
    botStore.activeBot.getPairHistory(payload);
  } else {
    botStore.activeBot.getPairCandles({
      pair,
      timeframe: finalTimeframe.value,
      columns,
    });
  }
}

const exchange = ref<{
  customExchange: boolean;
  selectedExchange: ExchangeSelection;
}>({
  customExchange: false,
  selectedExchange: {
    exchange: botStore.activeBot.botState.exchange,
    trade_mode: {
      margin_mode: MarginMode.NONE,
      trading_mode: TradingMode.SPOT,
    },
  },
});

const markets = ref<Markets | null>(null);
</script>

<template>
  <div class="flex flex-col h-full">
    <div v-if="botStore.activeBot.isWebserverMode" class="md:mx-3 mt-2 px-1">
      <Panel header="Live Data Settings" toggleable>
        <div class="mb-2 border dark:border-surface-700 border-surface-300 rounded-md p-2 text-start">
          <div class="flex flex-row gap-5">
            <BaseCheckbox v-model="exchange.customExchange" class="mb-2">
              Custom Exchange
            </BaseCheckbox>
            <span v-show="!exchange.customExchange">
              Current Exchange:
              {{ botStore.activeBot.botState.exchange }}
              {{ botStore.activeBot.botState.trading_mode }}
            </span>
          </div>
          <Transition name="fade">
            <ExchangeSelect v-show="exchange.customExchange" v-model="exchange.selectedExchange" />
          </Transition>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 mx-1 gap-1 md:gap-2">
          <div class="text-start md:me-1 col-span-2">
            <span>Strategy</span>
            <StrategySelect v-model="chartStore.strategy" class="mt-1 mb-1"></StrategySelect>
            <BaseCheckbox v-model="chartStore.useLiveData" class="align-self-center" disabled>
              Use Live Data (forced)
            </BaseCheckbox>
          </div>
          <div class="flex flex-col text-start">
            <span>Timeframe</span>
            <TimeframeSelect v-model="chartStore.selectedTimeframe" class="mt-1" />
          </div>
        </div>
      </Panel>
    </div>

    <div class="md:mx-2 mt-2 pb-1 h-full">
      <CandleChartContainer
        :available-pairs="availablePairs"
        :historic-view="botStore.activeBot.isWebserverMode"
        :timeframe="finalTimeframe"
        :trades="botStore.activeBot.allTrades"
        :strategy="botStore.activeBot.isWebserverMode ? chartStore.strategy : undefined"
        @refresh-data="refreshOHLCV"
      />
    </div>
  </div>
</template>
