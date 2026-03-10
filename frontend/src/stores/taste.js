import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useTasteStore = defineStore('taste', () => {
  // 온보딩에서 수집하는 취향 프로파일
  const tannin = ref(2.5)
  const acidity = ref(2.5)
  const body = ref(2.5)
  const sweetness = ref(2.5)
  const preferredAromas = ref([])
  const dietaryRestrictions = ref([])

  function setTasteProfile(profile) {
    tannin.value = profile.tannin ?? tannin.value
    acidity.value = profile.acidity ?? acidity.value
    body.value = profile.body ?? body.value
    sweetness.value = profile.sweetness ?? sweetness.value
    preferredAromas.value = profile.preferredAromas ?? preferredAromas.value
    dietaryRestrictions.value = profile.dietaryRestrictions ?? dietaryRestrictions.value
  }

  function toggleAroma(aroma) {
    const idx = preferredAromas.value.indexOf(aroma)
    if (idx === -1) {
      preferredAromas.value.push(aroma)
    } else {
      preferredAromas.value.splice(idx, 1)
    }
  }

  function toggleRestriction(restriction) {
    const idx = dietaryRestrictions.value.indexOf(restriction)
    if (idx === -1) {
      dietaryRestrictions.value.push(restriction)
    } else {
      dietaryRestrictions.value.splice(idx, 1)
    }
  }

  function getRadarData() {
    return {
      labels: ['타닌', '산미', '바디감', '당도'],
      datasets: [
        {
          label: '내 취향',
          data: [tannin.value, acidity.value, body.value, sweetness.value],
          backgroundColor: 'rgba(114, 47, 55, 0.2)',
          borderColor: '#722F37',
          borderWidth: 2,
          pointBackgroundColor: '#722F37',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: '#722F37',
        },
      ],
    }
  }

  return {
    tannin,
    acidity,
    body,
    sweetness,
    preferredAromas,
    dietaryRestrictions,
    setTasteProfile,
    toggleAroma,
    toggleRestriction,
    getRadarData,
  }
})
