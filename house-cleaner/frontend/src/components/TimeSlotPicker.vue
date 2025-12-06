<template>
  <div class="time-slot-picker">
    <label class="label">Select Date & Time</label>
    <div class="date-time-container">
      <!-- Date Selection -->
      <div class="date-selector">
        <input 
          type="date" 
          v-model="selectedDate" 
          :min="minDate"
          @change="onDateChange"
          class="date-input"
        />
      </div>

      <!-- Time Slot Selection -->
      <div v-if="selectedDate" class="time-slots">
        <div class="time-slots-header">
          <span class="slots-label">Available Time Slots</span>
          <span class="duration-hint">({{ slotDuration }} min intervals)</span>
        </div>
        <div class="slots-grid">
          <button
            v-for="slot in availableSlots"
            :key="slot.value"
            type="button"
            :class="['time-slot-btn', { active: selectedTime === slot.value, disabled: slot.disabled }]"
            @click="selectSlot(slot)"
            :disabled="slot.disabled"
          >
            {{ slot.label }}
          </button>
        </div>
        <div v-if="availableSlots.length === 0" class="no-slots">
          No available slots for this date
        </div>
      </div>
    </div>
    <div v-if="selectedDateTime" class="selected-info">
      <span>Selected: <strong>{{ formattedDateTime }}</strong></span>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'TimeSlotPicker',
  props: {
    modelValue: String, // ISO datetime string
    serviceDuration: {
      type: Number,
      default: 60
    },
    slotDuration: {
      type: Number,
      default: 30 // 30-minute increments
    },
    businessHoursStart: {
      type: Number,
      default: 8 // 8 AM
    },
    businessHoursEnd: {
      type: Number,
      default: 19 // 7 PM
    },
    minLeadTimeHours: {
      type: Number,
      default: 3
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const selectedDate = ref('')
    const selectedTime = ref('')
    
    // Calculate minimum date (today)
    const minDate = computed(() => {
      const today = new Date()
      return today.toISOString().split('T')[0]
    })

    // Parse ISO string to get date and time
    if (props.modelValue) {
      try {
        const dt = new Date(props.modelValue)
        selectedDate.value = dt.toISOString().split('T')[0]
        selectedTime.value = dt.toTimeString().slice(0, 5) // HH:MM format
      } catch (e) {
        console.error('Error parsing modelValue:', e)
      }
    }

    // Generate available time slots for selected date
    const availableSlots = computed(() => {
      if (!selectedDate.value) return []

      const slots = []
      const now = new Date()
      const selected = new Date(selectedDate.value)
      const isToday = selected.toDateString() === now.toDateString()
      
      // Calculate minimum start time (current time + lead time)
      const minStartTime = new Date(now.getTime() + props.minLeadTimeHours * 60 * 60 * 1000)

      for (let hour = props.businessHoursStart; hour < props.businessHoursEnd; hour++) {
        for (let minute = 0; minute < 60; minute += props.slotDuration) {
          const slotTime = new Date(selected)
          slotTime.setHours(hour, minute, 0, 0)
          
          // Calculate end time based on service duration
          const endTime = new Date(slotTime.getTime() + props.serviceDuration * 60 * 1000)
          
          // Check if slot is valid
          const isDisabled = 
            (isToday && slotTime < minStartTime) || // Too soon if today
            endTime.getHours() > props.businessHoursEnd || // Would extend past business hours
            (endTime.getHours() === props.businessHoursEnd && endTime.getMinutes() > 0)

          const timeStr = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`
          
          slots.push({
            label: formatTimeLabel(hour, minute),
            value: timeStr,
            disabled: isDisabled,
            datetime: slotTime
          })
        }
      }

      return slots
    })

    // Format time label (e.g., "9:00 AM")
    function formatTimeLabel(hour, minute) {
      const period = hour >= 12 ? 'PM' : 'AM'
      const displayHour = hour > 12 ? hour - 12 : hour === 0 ? 12 : hour
      return `${displayHour}:${String(minute).padStart(2, '0')} ${period}`
    }

    // Select a time slot
    function selectSlot(slot) {
      if (slot.disabled) return
      selectedTime.value = slot.value
      emitDateTime()
    }

    // Handle date change
    function onDateChange() {
      selectedTime.value = ''
      emitDateTime()
    }

    // Emit ISO datetime string
    function emitDateTime() {
      if (!selectedDate.value || !selectedTime.value) {
        emit('update:modelValue', '')
        return
      }

      const [hours, minutes] = selectedTime.value.split(':').map(Number)
      const datetime = new Date(selectedDate.value)
      datetime.setHours(hours, minutes, 0, 0)
      
      // Convert to ISO string (backend expects UTC)
      emit('update:modelValue', datetime.toISOString())
    }

    // Watch for changes and emit
    watch([selectedDate, selectedTime], () => {
      emitDateTime()
    })

    // Formatted display datetime
    const formattedDateTime = computed(() => {
      if (!selectedDate.value || !selectedTime.value) return ''
      try {
        const [hours, minutes] = selectedTime.value.split(':').map(Number)
        const dt = new Date(selectedDate.value)
        dt.setHours(hours, minutes)
        return dt.toLocaleString('en-US', {
          weekday: 'short',
          month: 'short',
          day: 'numeric',
          year: 'numeric',
          hour: 'numeric',
          minute: '2-digit'
        })
      } catch (e) {
        return ''
      }
    })

    return {
      selectedDate,
      selectedTime,
      minDate,
      availableSlots,
      formattedDateTime,
      selectSlot,
      onDateChange
    }
  }
}
</script>

<style scoped>
.time-slot-picker {
  margin-bottom: var(--spacing-lg);
}

.label {
  display: block;
  font-weight: 600;
  color: #1f2937 !important;
  margin-bottom: var(--spacing-md);
  font-size: var(--font-size-base);
}

.date-time-container {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.date-input {
  width: 100%;
  padding: var(--spacing-md);
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: var(--font-size-base);
  font-family: var(--font-family);
  cursor: pointer;
  transition: all var(--transition-base);
  background: #ffffff !important;
  color: #1f2937 !important;
}

.date-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
  background: #ffffff !important;
  color: #1f2937 !important;
}

.time-slots {
  width: 100%;
}

.time-slots-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.slots-label {
  font-weight: 600;
  color: #1f2937 !important;
}

.duration-hint {
  font-size: var(--font-size-sm);
  color: #6b7280 !important;
}

.slots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: var(--spacing-sm);
  max-height: 300px;
  overflow-y: auto;
  padding: var(--spacing-sm);
}

.time-slot-btn {
  padding: var(--spacing-md);
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius);
  background: #ffffff !important;
  color: #1f2937 !important;
  font-size: var(--font-size-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-base);
}

.time-slot-btn:hover:not(.disabled) {
  border-color: var(--color-primary);
  background: rgba(59, 130, 246, 0.05);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.time-slot-btn.active {
  border-color: var(--color-primary);
  background: var(--color-primary) !important;
  color: #ffffff !important;
  box-shadow: var(--shadow);
}

.time-slot-btn.disabled {
  opacity: 0.4;
  cursor: not-allowed;
  background: var(--bg-subtle);
}

.no-slots {
  padding: var(--spacing-lg);
  text-align: center;
  color: #6b7280 !important;
  background: #f9fafb;
  border-radius: var(--border-radius);
  font-style: italic;
}

.selected-info {
  margin-top: var(--spacing-md);
  padding: var(--spacing-md);
  background: rgba(16, 185, 129, 0.1);
  border-left: 4px solid var(--color-success);
  border-radius: var(--border-radius);
  color: #1f2937 !important;
  font-size: var(--font-size-sm);
}

.selected-info strong {
  color: #059669 !important;
}

@media (max-width: 768px) {
  .slots-grid {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  }
  
  .time-slots-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-xs);
  }
}
</style>

