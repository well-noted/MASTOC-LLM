;;; ============================================================
;;; MASTOC-LLM v1.0
;;; Multi-Agent System Tragedy of the Commons
;;; with LLM-based agent decision-making
;;;
;;; Conditions:
;;;   "baseline"  — rule-based best-response heuristic (approximates original Nash)
;;;   "full-gabm" — all agents use LLM
;;;   "hybrid"    — hybrid-fraction agents use LLM; rest use best-response
;;;
;;; Requires NetLogo 6.2+ with the py extension.
;;; Python bridge: mastoc_llm_bridge.py (must be in the same directory)
;;; ============================================================

extensions [ py ]

patches-own [ elapsed-growth-time rand-number ]

turtles-own [
  payoff Nash-list list-of-Nash-lists forage grazing-counter action M ki
  payoff-total w owner derived-payoff final-total reduced-list-of-Nash-lists
  random-number payoff-total2 comparison-list-alpha comparison-list-beta id
  payoff-total3 xi C payoff-total-coop add-fairness previous-action d-neg d-pos d-zero
  add-reciprocity list-of-agent-actions minus-counter equal-counter plus-counter
  add-conformity add-a-cow-payoff-list remove-a-cow-payoff-list let-equal-payoff-list
  add-a-cow-minimum-payoff let-equal-minimum-payoff remove-a-cow-minimum-payoff-perc
  let-equal-minimum-payoff-perc add-a-cow-minimum-payoff-perc remove-a-cow-minimum-payoff
  list-of-agent-payoffs list-of-calc-agent-payoffs current-value list-of-final-agent-payoffs
  savings initial-cattle
  ;; --- NEW for MASTOC-LLM ---
  is-llm-agent    ;; TRUE if this agent uses LLM decision-making
  outgoing-message ;; message to broadcast to neighbours this round
]

globals [
  nrActions kk counter total j step P K DiedK previous-list next-list b current f d
  nrCombinations u-list payoff-list y yy nr v jj ii list-of-payoff-lists selected-Nash-equilibrium
  gg list-of-numbering-lists numbering-list final-action-list not-valid rr lengthlist aa ss
  final-payoff-list mm final-numbering-list product nn first-equilibrium second-equilibrium
  first-is-larger bb non-is-dominated index rrr ended equal sd Capacity sum-action
  new-grass-regeneration-period vv loss-list maxV Veg grass-initial-cows grass-after-cows
  cost-of-action Veg1 Veg2 remove-one-cow-value minus-value equal-value plus-value
  list-of-agent-actions-length item-of-final-payoff-list final-agent-payoff-list
  count-human count-item count-global pressure
  ;; --- NEW for MASTOC-LLM ---
  llm-ready       ;; TRUE once the Python bridge is initialised
  max-patches     ;; total patch count (cached at setup)
]

breed [ cows cow ]
breed [ humans human ]


;;; ============================================================
;;; SETUP
;;; ============================================================

to setup
  ca
  set llm-ready false
  set max-patches count patches

  create-humans 3
  set nrActions 3
  ask human 0 [ set ki agent0-initial-cows  set action 1 set initial-cattle ki ]
  ask human 1 [ set ki agent1-initial-cows  set action 1 set initial-cattle ki ]
  ask human 2 [ set ki agent2-initial-cows  set action 1 set initial-cattle ki ]
  set K sum [ ki ] of humans
  set P 2
  ask humans [ set previous-action (random 3) - 1 ]

  ;; Mark LLM agents based on condition
  ifelse condition = "full-gabm" [
    ask humans [ set is-llm-agent true ]
  ] [
    ifelse condition = "hybrid" [
      ;; Designate hybrid-fraction of agents (rounded) as LLM agents
      ;; Initialise all to false first so none carry a numeric 0 default
      ask humans [ set is-llm-agent false ]
      let n-llm max (list 1 round (count humans * hybrid-fraction))
      ask n-of n-llm humans [ set is-llm-agent true ]
    ] [
      ;; baseline — no LLM agents
      ask humans [ set is-llm-agent false ]
    ]
  ]

  ask humans [
    set list-of-agent-actions []
    set color white
    set shape "person"
    set size 3
    setxy random-xcor random-ycor
    hatch-cows ki [
      set color brown set shape "cow" set size 3
      setxy random-xcor random-ycor
      set owner myself
    ]
    set outgoing-message ""
  ]

  ask n-of round (count patches * initial-grassland / 100) patches [
    set pcolor green - 2
  ]

  ask cows [ set color brown set shape "cow" set size 3 setxy random-xcor random-ycor ]
  set step 0
  set DiedK 3

  ask humans [
    set add-a-cow-payoff-list []
    set let-equal-payoff-list []
    set remove-a-cow-payoff-list []
    set list-of-agent-payoffs []
    set list-of-calc-agent-payoffs []
  ]

  ;; Initialise Python bridge (only needed for non-baseline conditions)
  if condition != "baseline" [ setup-python-bridge ]

  reset-ticks
  generate-payoffs
end


;;; ============================================================
;;; PYTHON BRIDGE INITIALISATION
;;; ============================================================

to setup-python-bridge
  py:setup py:python3
  ;; Load the bridge module (must be in the same directory as the .nlogo file)
  py:run "import sys, os; sys.path.insert(0, os.getcwd())"
  py:run "import mastoc_llm_bridge as bridge"

  ;; Pass string parameters via py:set to avoid quoting/escaping issues
  py:set "cfg_agent_backends" (list agent0-backend agent1-backend agent2-backend)
  py:set "cfg_agent_models"   (list agent0-model   agent1-model   agent2-model)
  py:set "cfg_condition"           condition
  py:set "cfg_memory_length"       memory-length
  py:set "cfg_detect_institutions" detect-institutions    ;; NetLogo bool → Python bool
  py:set "cfg_institution_interval" institution-check-interval

  py:set "cfg_system_prompt"   system-prompt-override
  py:set "cfg_ollama_base_url" ollama-base-url
  let status py:runresult (word
    "bridge.configure("
    "agent_backends=cfg_agent_backends, "
    "agent_models=cfg_agent_models, "
    "condition=cfg_condition, "
    "memory_length=cfg_memory_length, "
    "log_dir='logs', "
    "detect_institutions=cfg_detect_institutions, "
    "institution_every_n_ticks=cfg_institution_interval, "
    "system_prompt_override=cfg_system_prompt, "
    "ollama_base_url=cfg_ollama_base_url"
    ")")
  show status

  ;; Log all experiment parameters to run_meta.json for reproducibility
  py:set "param_keys" (list
    "cooperation_level" "fairness_concerning_me" "fairness_concerning_others"
    "positive_reciprocity" "negative_reciprocity" "risk_aversion_level"
    "initial_grassland" "initial_grass_growth_rate" "cow_forage_requirement"
    "memory_length" "initial_cows_agent0" "initial_cows_agent1" "initial_cows_agent2"
    "ollama_base_url")
  py:set "param_vals" (list
    cooperation-level fairness-concerning-me fairness-concerning-others
    positive-reciprocity negative-reciprocity risk-aversion-level
    initial-grassland initial-grass-growth-rate cow-forage-requirement
    memory-length agent0-initial-cows agent1-initial-cows agent2-initial-cows
    ollama-base-url)
  py:run "bridge.log_params(dict(zip(param_keys, param_vals)))"

  ;; Register each LLM agent with the bridge
  ask humans with [ is-llm-agent ] [
    py:run (word "bridge.init_agent(" who ")")
  ]

  set llm-ready true
end


;;; ============================================================
;;; MAIN SIMULATION LOOP
;;; ============================================================

to simulation
  tick
  set step step + 1

  ;; Reset per-tick payoff accumulators
  ask humans [
    set add-a-cow-payoff-list []
    set let-equal-payoff-list []
    set remove-a-cow-payoff-list []
    set list-of-agent-payoffs []
    set list-of-calc-agent-payoffs []
  ]

  ;; Always compute payoff matrix — provides context for all agent types
  generate-payoffs

  ;; ── Decision step (condition-dependent) ──────────────────────────────────
  ifelse condition = "baseline" [
    ;; Rule-based best-response for all agents (no LLM)
    ask humans [ rule-based-decide ]
  ] [
    ifelse condition = "full-gabm" [
      ;; LLM decision for all agents
      ask humans [ llm-decide ]
    ] [
      ;; Hybrid: LLM agents reason via bridge, rule-based agents use heuristic
      ask humans with [ is-llm-agent ] [ llm-decide ]
      ask humans with [ not is-llm-agent ] [ rule-based-decide ]
    ]
    ;; Broadcast messages from LLM agents to their neighbours
    broadcast-messages
  ]

  ;; ── Execute decisions ─────────────────────────────────────────────────────
  change-number-of-cows
  graze

  ;; ── Plots & resource state ────────────────────────────────────────────────
  set pressure count patches with [ pcolor = black ] / count patches
  set-current-plot "Grazing pressure"
  set-current-plot-pen "pressure"
  plotxy step pressure

  grass-regrowth
  plot-data
  export-data

  ;; ── End-of-round logging via bridge ──────────────────────────────────────
  if condition != "baseline" and llm-ready [
    let _status py:runresult (word
      "bridge.end_round("
      ticks ", "
      count patches with [ pcolor = green - 2 ] ", "
      max-patches ", "
      count cows ", "
      pressure ", "
      count cows with [ owner = human 0 ] ", "
      count cows with [ owner = human 1 ] ", "
      count cows with [ owner = human 2 ]
      ")")
  ]

  if (not run-indefinitely) and (ticks >= num-rounds) [ close-bridge stop ]
end


;;; ============================================================
;;; DECISION PROCEDURES
;;; ============================================================

;; ── LLM agent: call Python bridge ─────────────────────────────────────────
to llm-decide
  ;; Build context list and pass to bridge via py:set (avoids NetLogo string escaping)
  let neighbour-ids   map [ h -> [who] of h ] sort other humans
  let neighbour-herds map [ h -> [ki] of h ] sort other humans
  let neighbour-acts  map [ h -> [previous-action] of h ] sort other humans

  ;; Payoff estimates from current generate-payoffs run
  let p-add    (ifelse-value (length add-a-cow-payoff-list > 0)
                  [ min add-a-cow-payoff-list ] [ 0 ])
  let p-keep   (ifelse-value (length let-equal-payoff-list > 0)
                  [ min let-equal-payoff-list ] [ 0 ])
  let p-remove (ifelse-value (length remove-a-cow-payoff-list > 0)
                  [ min remove-a-cow-payoff-list ] [ 0 ])

  py:set "ctx" (list
    who ticks
    count patches with [ pcolor = green - 2 ]
    max-patches
    ki previous-action payoff
    neighbour-ids neighbour-herds neighbour-acts
    p-add p-keep p-remove
    fairness-concerning-me fairness-concerning-others
    cooperation-level negative-reciprocity positive-reciprocity
    conformity-level risk-aversion-level
  )

  let chosen-action py:runresult "bridge.decide_from_context(ctx)"
  set action chosen-action
  set previous-action action
  set list-of-agent-actions lput action list-of-agent-actions

  ;; Retrieve outgoing message
  set outgoing-message py:runresult (word "bridge.get_outgoing_message(" who ")")
end


;; ── Rule-based agent: Python best-response heuristic ─────────────────────
to rule-based-decide
  ;; Reuse the same ctx structure so bridge.baseline_decide() can be called
  ;; from Python even for rule-based agents (consistent logging path).
  let neighbour-ids   map [ h -> [who] of h ] sort other humans
  let neighbour-herds map [ h -> [ki] of h ] sort other humans
  let neighbour-acts  map [ h -> [previous-action] of h ] sort other humans

  let p-add    (ifelse-value (length add-a-cow-payoff-list > 0)
                  [ min add-a-cow-payoff-list ] [ 0 ])
  let p-keep   (ifelse-value (length let-equal-payoff-list > 0)
                  [ min let-equal-payoff-list ] [ 0 ])
  let p-remove (ifelse-value (length remove-a-cow-payoff-list > 0)
                  [ min remove-a-cow-payoff-list ] [ 0 ])

  ifelse condition = "baseline" [
    ;; Pure NetLogo best-response — no Python call needed for baseline
    let best-action 0
    let best-payoff p-keep
    if p-add > best-payoff [ set best-action 1  set best-payoff p-add ]
    if p-remove > best-payoff [ set best-action -1 ]
    ;; Risk-aversion noise: risk-averse agents occasionally prefer KEEP over ADD
    if best-action = 1 and random-float 1 < risk-aversion-level * 0.3 [
      set best-action 0
    ]
    set action best-action
  ] [
    ;; Hybrid condition: call Python bridge so rule-based agents are logged too
    py:set "ctx" (list
      who ticks
      count patches with [ pcolor = green - 2 ]
      max-patches
      ki previous-action payoff
      neighbour-ids neighbour-herds neighbour-acts
      p-add p-keep p-remove
      fairness-concerning-me fairness-concerning-others
      cooperation-level negative-reciprocity positive-reciprocity
      conformity-level risk-aversion-level
    )
    set action py:runresult "bridge.baseline_decide(ctx)"
  ]

  set previous-action action
  set list-of-agent-actions lput action list-of-agent-actions
  set outgoing-message ""
end


;;; ============================================================
;;; COMMUNICATION
;;; ============================================================

to broadcast-messages
  ;; Each LLM agent that has a non-empty outgoing message delivers it to all neighbours.
  ;; Use py:set for the message string to avoid ALL quoting/escaping edge cases.
  ask humans with [ is-llm-agent ] [
    if outgoing-message != "" [
      let sender who
      let msg outgoing-message
      ask other humans [
        py:set "bcast_from"    sender
        py:set "bcast_to"      who
        py:set "bcast_content" msg
        py:run "bridge.deliver_message(bcast_from, bcast_to, bcast_content)"
      ]
    ]
  ]
end


;;; ============================================================
;;; CLEANUP
;;; ============================================================

to close-bridge
  if condition != "baseline" and llm-ready [
    let _msg py:runresult "bridge.close()"
    show _msg
  ]
end


;;; ============================================================
;;; PAYOFF GENERATION  (unchanged from original MASTOC logic)
;;; ============================================================

to generate-payoffs
  ask humans [ set ki count cows with [ owner = myself ] ]
  set K sum [ ki ] of humans
  set list-of-payoff-lists []
  set list-of-numbering-lists []
  set nrCombinations power nrActions (count humans)
  set u-list n-values count humans [ i -> -1 ]
  set payoff-list n-values count humans [ i -> 0 ]
  set numbering-list n-values count humans [ i -> 0 ]

  while [ y < nrCombinations ] [
    while [ yy < count humans ] [
      if (y mod (power nrActions yy)) = 0 [
        set u-list replace-item yy u-list ((item yy u-list) + 1)
      ]
      set payoff-list replace-item yy payoff-list ((item yy u-list) mod nrActions)
      set numbering-list replace-item yy numbering-list ((item yy u-list) mod nrActions)
      if item yy payoff-list = 0 [ set payoff-list replace-item yy payoff-list 3 ]
      if item yy payoff-list = 1 [ set payoff-list replace-item yy payoff-list 0 ]
      if item yy payoff-list = 2 [ set payoff-list replace-item yy payoff-list -1 ]
      if item yy payoff-list = 3 [ set payoff-list replace-item yy payoff-list 1 ]
      set yy yy + 1
    ]
    set yy 0
    calculate-payoff payoff-list
    set list-of-payoff-lists lput payoff-list list-of-payoff-lists
    set list-of-numbering-lists lput numbering-list list-of-numbering-lists
    set y y + 1
  ]
  set y 0

  foreach sort humans [ h ->
    ask h [
      set remove-a-cow-minimum-payoff min remove-a-cow-payoff-list
      set let-equal-minimum-payoff    min let-equal-payoff-list
      set add-a-cow-minimum-payoff    min add-a-cow-payoff-list
      let denom sum (list remove-a-cow-minimum-payoff
                         let-equal-minimum-payoff
                         add-a-cow-minimum-payoff)
      if denom != 0 [
        set remove-a-cow-minimum-payoff-perc remove-a-cow-minimum-payoff / denom
        set let-equal-minimum-payoff-perc    let-equal-minimum-payoff    / denom
        set add-a-cow-minimum-payoff-perc    add-a-cow-minimum-payoff    / denom
      ]
    ]
  ]

  ;; Build final payoff lists (used for Nash calculation / LLM context)
  ;; Build risk-aversion-weighted final payoff lists (mirrors original MASTOC logic).
  ;; Each payoff = base_calc + raw * ra * risk_factor
  ;; where risk_factor depends on whether this action has the highest min-payoff
  ;; fraction (the agent's "best" option gets a higher weight under risk-aversion).
  set count-human 0
  ask humans [ set list-of-final-agent-payoffs [] ]
  while [ count-human < count humans ] [
    ask human count-human [
      set count-item 0
      ;; Cache the ordered percentages for readability
      let perc-list (list remove-a-cow-minimum-payoff-perc
                          let-equal-minimum-payoff-perc
                          add-a-cow-minimum-payoff-perc)
      let max-perc max perc-list

      while [ count-item < length list-of-calc-agent-payoffs ] [
        let base-payoff item count-item list-of-calc-agent-payoffs
        let raw-payoff  item count-item list-of-agent-payoffs
        let action-code item count-human item count-item list-of-numbering-lists

        ;; Select this action's minimum-payoff percentage (0=remove,1=keep,2=add)
        let this-perc ifelse-value (action-code = 0)
          [ remove-a-cow-minimum-payoff-perc ]
          [ ifelse-value (action-code = 1)
            [ let-equal-minimum-payoff-perc ]
            [ add-a-cow-minimum-payoff-perc ] ]

        ;; Risk factor: best option gets compound weight; others get a discount
        let risk-factor ifelse-value (this-perc = max-perc)
          [ this-perc + risk-aversion-level * (1 - this-perc) ]
          [ (1 - risk-aversion-level) * this-perc ]

        set current-value base-payoff + raw-payoff * risk-aversion-level * risk-factor
        set list-of-final-agent-payoffs lput current-value list-of-final-agent-payoffs
        set count-item count-item + 1
      ]
    ]
    set count-human count-human + 1
  ]
end


;;; ============================================================
;;; PAYOFF CALCULATION  (unchanged from original MASTOC logic)
;;; ============================================================

to calculate-payoff [ payoffs ]
  set d sum payoffs
  ask humans [ set xi item who payoffs ]
  ask humans [
    if xi = 1  [ set C cost K (K + 1) ]
    if xi = 0  [ set C 0 ]
    if xi = -1 [ set C cost K (K - 1) ]
  ]
  ask humans [ set payoff-total 0 ]
  foreach sort humans [ h ->
    ask h [ set payoff-total (ki + xi) * P - C ]
  ]

  ;; Cooperation adjustment
  ask humans [
    set payoff-total-coop
      (1 - cooperation-level) * payoff-total +
      cooperation-level * ((K + d) * P - sum [ C ] of humans)
  ]

  ;; Fairness adjustment
  foreach sort humans [ h ->
    ask h [
      set comparison-list-alpha []
      set comparison-list-beta  []
      set rrr 0
      while [ rrr < count humans ] [
        if human rrr != h [
          set comparison-list-alpha lput
            (max (list ([ payoff-total ] of human rrr - payoff-total) 0))
            comparison-list-alpha
          set comparison-list-beta lput
            (max (list (payoff-total - [ payoff-total ] of human rrr) 0))
            comparison-list-beta
        ]
        set rrr rrr + 1
      ]
      set rrr 0
    ]
  ]
  ask humans [
    set add-fairness
      fairness-concerning-me    / (count humans - 1) * sum comparison-list-alpha +
      fairness-concerning-others / (count humans - 1) * sum comparison-list-beta
  ]
  let total-payoff sum [ payoff-total ] of humans
  if total-payoff != 0 [
    ask humans [
      set add-fairness add-fairness / total-payoff * (count humans - 1) * payoff-total
    ]
  ]

  ;; Reciprocity adjustment
  ask humans [
    set d-pos count other humans with [ previous-action = 1 ]
    set d-neg count other humans with [ previous-action = -1 ]
    set d-zero count other humans with [ previous-action = 0 ]
    if xi = 1  [
      set add-reciprocity payoff-total *
        (negative-reciprocity * (d-pos + 0.5 * d-zero) / (count humans - 1))
    ]
    if xi = -1 [
      set add-reciprocity payoff-total *
        (positive-reciprocity * (d-neg + 0.5 * d-zero) / (count humans - 1))
    ]
    if xi = 0  [
      set add-reciprocity payoff-total * 0.5 * (
        (negative-reciprocity * (d-pos + 0.5 * d-zero) / (count humans - 1)) +
        (positive-reciprocity * (d-neg + 0.5 * d-zero) / (count humans - 1)))
    ]
  ]

  ;; Conformity adjustment
  ask humans [
    ifelse length list-of-agent-actions > 0
      [ set list-of-agent-actions-length length list-of-agent-actions ]
      [ set list-of-agent-actions-length 1 ]
    set minus-counter 0
    set equal-counter 0
    set plus-counter  0
    foreach list-of-agent-actions [ a ->
      if a = -1 [ set minus-counter minus-counter + 1 ]
      if a = 0  [ set equal-counter equal-counter + 1 ]
      if a = 1  [ set plus-counter  plus-counter  + 1 ]
    ]
  ]
  set minus-value sum [ minus-counter ] of humans / (count humans * list-of-agent-actions-length)
  set equal-value sum [ equal-counter ] of humans / (count humans * list-of-agent-actions-length)
  set plus-value  sum [ plus-counter  ] of humans / (count humans * list-of-agent-actions-length)

  ask humans [
    if xi = -1 [ set add-conformity conformity-level * payoff-total * minus-value ]
    if xi = 0  [ set add-conformity conformity-level * payoff-total * equal-value ]
    if xi = 1  [ set add-conformity conformity-level * payoff-total * plus-value  ]
  ]

  ;; Accumulate payoff lists by action
  foreach sort humans [ h ->
    ask h [
      set list-of-agent-payoffs lput payoff-total list-of-agent-payoffs
    ]
  ]
  ask humans [
    if xi = -1 [ set remove-a-cow-payoff-list lput payoff-total remove-a-cow-payoff-list ]
    if xi = 0  [ set let-equal-payoff-list    lput payoff-total let-equal-payoff-list    ]
    if xi = 1  [ set add-a-cow-payoff-list    lput payoff-total add-a-cow-payoff-list    ]
  ]

  ;; Final payoff with all adjustments
  ask humans [
    set payoff-total payoff-total-coop - add-fairness + add-reciprocity + add-conformity
  ]
  foreach sort humans [ h ->
    ask h [
      set list-of-calc-agent-payoffs lput payoff-total list-of-calc-agent-payoffs
    ]
  ]
end


;;; ============================================================
;;; COW MANAGEMENT
;;; ============================================================

to change-number-of-cows
  ask humans [
    if action = 1 [
      hatch-cows 1 [
        set color brown set shape "cow" set size 3
        setxy random-xcor random-ycor
        set owner myself
      ]
    ]
    if action = -1 [
      if any? cows with [ owner = myself ] [
        ask one-of cows with [ owner = myself ] [ die ]
      ]
    ]
  ]
end


;;; ============================================================
;;; GRAZING
;;; ============================================================

to graze
  ask cows [ set forage 0 ]
  ask cows [
    while [ (forage < cow-forage-requirement) and
            (any? patches with [ pcolor = green - 2 ]) ] [
      move-to min-one-of patches with [ pcolor = green - 2 ] [ distance myself ]
      ask patch-here [ set pcolor black set elapsed-growth-time 0 ]
      set forage forage + 1
    ]
    if forage < cow-forage-requirement [ die ]
  ]
end


;;; ============================================================
;;; GRASS REGROWTH  (logistic model)
;;; ============================================================

to grass-regrowth
  set Veg count patches with [ pcolor = green - 2 ]
  set maxV count patches
  let new-grass round (Veg * (1 + (initial-grass-growth-rate * Veg * (1 - (Veg / maxV)))) - Veg)
  let n-grow min (list new-grass count patches with [ pcolor = black ])
  if n-grow > 0 [
    ask n-of n-grow patches with [ pcolor = black ] [ set pcolor green - 2 ]
  ]
end


;;; ============================================================
;;; COST FUNCTION  (unchanged)
;;; ============================================================

to-report cost [ initial-cows after-cows ]
  set Veg1 count patches with [ pcolor = green - 2 ] - initial-cows * cow-forage-requirement
  set Veg2 count patches with [ pcolor = green - 2 ] - after-cows * cow-forage-requirement
  set maxV count patches
  set grass-initial-cows
    (max list 0 Veg1) * (1 + (initial-grass-growth-rate * Veg1 * (1 - (Veg1 / maxV))))
  set grass-after-cows
    (max list 0 Veg2) * (1 + (initial-grass-growth-rate * Veg2 * (1 - (Veg2 / maxV))))
  set cost-of-action
    (grass-initial-cows - grass-after-cows) / (cow-forage-requirement * count humans) * P
  report cost-of-action
end


;;; ============================================================
;;; HELPERS
;;; ============================================================

to-report power [ a q ]
  set nr 1
  while [ v < q ] [ set nr nr * a  set v v + 1 ]
  set v 0
  report nr
end


;;; ============================================================
;;; DATA EXPORT  (extended for LLM conditions)
;;; ============================================================

to plot-data
  set-current-plot "Plot"
  set-current-plot-pen "Patches"
  plotxy step count patches with [ pcolor = green - 2 ]
  set-current-plot-pen "Cows"
  plotxy step count cows
end

to export-data
  ;; Existing MASTOC flat-file exports (maintained for backward compatibility)
  file-open "Data/Sensitivity-pressure.txt"
  if ticks = 1 [
    file-print " "
    file-print (word "Condition: " condition)
    file-print (word "initial cows "
      [initial-cattle] of human 0 " "
      [initial-cattle] of human 1 " "
      [initial-cattle] of human 2)
    file-print (word "forage: " cow-forage-requirement)
    file-print (word "grass: "  initial-grassland)
    file-print (word "growth: " initial-grass-growth-rate)
    file-print (word "fairness me: "     fairness-concerning-me)
    file-print (word "fairness others: " fairness-concerning-others)
    file-print (word "cooperation: "     cooperation-level)
    file-print (word "recip neg: "       negative-reciprocity)
    file-print (word "recip pos: "       positive-reciprocity)
    file-print (word "conformity: "      conformity-level)
    file-print (word "risk aversion: "   risk-aversion-level)
  ]
  file-print pressure
  file-close

  file-open "Data/1-gain-agent0.txt"
  if ticks = 1 [ file-print (word "Condition: " condition) ]
  file-print count cows with [ owner = human 0 ]
  file-close

  file-open "Data/1-gain-agent1.txt"
  if ticks = 1 [ file-print (word "Condition: " condition) ]
  file-print count cows with [ owner = human 1 ]
  file-close

  file-open "Data/1-gain-agent2.txt"
  if ticks = 1 [ file-print (word "Condition: " condition) ]
  file-print count cows with [ owner = human 2 ]
  file-close

  file-open "Data/1-count-cows.txt"
  if ticks = 1 [ file-print (word "Condition: " condition) ]
  file-print count cows
  file-close
end


@#$#@#$#@
GRAPHICS-WINDOW
613
10
1144
562
16
16
15.8
1
10
1
1
1
0
0
0
1
-16
16
-16
16
0
0
1
ticks
30.0

BUTTON
8
10
216
43
NIL
setup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
8
47
216
80
NIL
simulation
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

SLIDER
8
117
216
150
cow-forage-requirement
cow-forage-requirement
0
50
2
1
1
NIL
HORIZONTAL

SLIDER
8
156
216
189
initial-grassland
initial-grassland
0
100
100
1
1
NIL
HORIZONTAL

SLIDER
8
195
216
228
initial-grass-growth-rate
initial-grass-growth-rate
0
0.1
0.001
0.0001
1
NIL
HORIZONTAL

PLOT
221
10
607
276
Plot
Time
Number
0.0
10.0
0.0
100.0
true
true
"" ""
PENS
"Patches" 1.0 0 -10899396 true "" ""
"Cows" 1.0 0 -6459832 true "" ""

PLOT
221
281
607
558
Grazing pressure
Time
Pressure
0.0
10.0
0.0
1.0
true
false
"" ""
PENS
"pressure" 1.0 0 -16777216 true "" ""

TEXTBOX
11
96
161
114
System parameters:
11
0.0
1

TEXTBOX
7
266
230
294
Socio-psychological dispositions:
11
0.0
1

TEXTBOX
7
490
230
514
LLM / Condition settings:
11
0.0
1

SLIDER
6
285
211
318
fairness-concerning-me
fairness-concerning-me
0
1
0
0.01
1
NIL
HORIZONTAL

SLIDER
5
326
211
359
fairness-concerning-others
fairness-concerning-others
0
1
1
0.01
1
NIL
HORIZONTAL

SLIDER
5
367
212
400
cooperation-level
cooperation-level
0
1
1
0.01
1
NIL
HORIZONTAL

SLIDER
5
407
213
440
negative-reciprocity
negative-reciprocity
0
1
0
0.01
1
NIL
HORIZONTAL

SLIDER
5
447
213
480
positive-reciprocity
positive-reciprocity
0
1
1
0.01
1
NIL
HORIZONTAL

SLIDER
4
484
213
517
conformity-level
conformity-level
0
1
0
0.01
1
NIL
HORIZONTAL

SLIDER
5
524
212
557
risk-aversion-level
risk-aversion-level
0
1
1
0.01
1
NIL
HORIZONTAL

CHOOSER
8
510
216
555
condition
condition
"baseline" "full-gabm" "hybrid"
0

CHOOSER
8
558
108
618
agent0-backend
agent0-backend
"anthropic" "openai" "ollama" "ollama-native" "google"
0

INPUTBOX
110
558
216
618
agent0-model
claude-sonnet-4-6
1
0
String

CHOOSER
8
620
108
680
agent1-backend
agent1-backend
"anthropic" "openai" "ollama" "ollama-native" "google"
0

INPUTBOX
110
620
216
680
agent1-model
claude-sonnet-4-6
1
0
String

CHOOSER
8
682
108
742
agent2-backend
agent2-backend
"anthropic" "openai" "ollama" "ollama-native" "google"
0

INPUTBOX
110
682
216
742
agent2-model
claude-sonnet-4-6
1
0
String

SLIDER
8
744
216
777
hybrid-fraction
hybrid-fraction
0
1
0.33
0.01
1
NIL
HORIZONTAL

SLIDER
8
780
216
813
memory-length
memory-length
1
10
5
1
1
rounds
HORIZONTAL

SWITCH
8
816
216
849
detect-institutions
detect-institutions
0
1
-1000

SLIDER
8
852
216
885
institution-check-interval
institution-check-interval
1
20
5
1
1
ticks
HORIZONTAL

SLIDER
8
888
216
921
agent0-initial-cows
agent0-initial-cows
1
60
5
1
1
cows
HORIZONTAL

SLIDER
8
924
216
957
agent1-initial-cows
agent1-initial-cows
1
60
15
1
1
cows
HORIZONTAL

SLIDER
8
960
216
993
agent2-initial-cows
agent2-initial-cows
1
60
25
1
1
cows
HORIZONTAL

INPUTBOX
8
996
216
1076
system-prompt-override
 
1
0
String

INPUTBOX
8
1086
432
1116
ollama-base-url
http://localhost:11434/v1
0
0
String

TEXTBOX
8
1150
216
1168
Simulation parameters:
11
0.0
1

SLIDER
8
1175
216
1208
num-rounds
num-rounds
1
500
120
1
1
rounds
HORIZONTAL

SWITCH
8
1215
216
1248
run-indefinitely
run-indefinitely
1
1
-1000

@#$#@#$#@
WHAT IS IT?
-----------
MASTOC-LLM is an extension of the MASTOC model (Multi-Agent System Tragedy of the Commons) that replaces the Nash-equilibrium decision mechanism with LLM-based reasoning for some or all agents.

Scientific question: Do Ostrom-style commons institutions (communication norms, graduated sanctions, coordination rules) emerge spontaneously from language-capable agents under resource pressure, without being hard-coded?

Three experimental conditions:
  1. Baseline    — rule-based best-response heuristic (reproduces classical tragedy as control)
  2. Full GABM   — all agents reason via LLM (Anthropic or Ollama)
  3. Hybrid      — a minority of LLM agents among rule-based majority

HOW IT WORKS
------------
Each tick:
1. Payoff matrix is computed for all action combinations (inherits MASTOC's socio-psychological disposition parameters: fairness, cooperation, reciprocity, conformity, risk-aversion).
2. Each agent decides:
   - LLM agents: send resource state + memory + neighbour messages to the LLM bridge; parse back action (-1/0/+1) and optional message.
   - Rule-based agents: myopic best-response (choose action with highest expected payoff).
3. LLM agents broadcast messages to neighbours (communication layer).
4. Actions are executed (cows added/removed), grazing occurs, grass regrows.
5. End-of-round: resource state and agent decisions logged; optional Ostrom institution detection classifies messages.

HOW TO USE IT
-------------
SETUP:
  1. Install NetLogo 6.2+ (https://netlogoweb.org)
  2. Install Python 3.9+ with: pip install anthropic openai
  3. Set ANTHROPIC_API_KEY environment variable (or start Ollama locally)
  4. Place MASTOC-LLM.nlogo and mastoc_llm_bridge.py in the same directory
  5. Create Data/ directory in the same folder
  6. Open MASTOC-LLM.nlogo in NetLogo

RUNNING:
  - Select a condition from the Condition chooser
  - Click Setup, then Simulation
  - CSV logs are written to logs/<run_id>/

OUTPUTS:
  - logs/<run_id>/resources.csv   — pool size, cow counts, pressure per tick
  - logs/<run_id>/decisions.csv   — agent decisions, reasoning, messages per tick
  - logs/<run_id>/institutions.csv — Ostrom institution detection scores per detected round
  - Data/Sensitivity-pressure.txt — grazing pressure time series (MASTOC-compatible)

CREDITS
-------
Based on MASTOC v1.1.0 by Bais et al. (CoMSES model #2283).
LLM bridge architecture inspired by swarm_gpt (Jimenez-Romero et al. 2025).
Extended for CAS 520 at Arizona State University.
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

airplane
true
0
Polygon -7500403 true true 150 0 135 15 120 60 120 105 15 165 15 195 120 180 135 240 105 270 120 285 150 270 180 285 210 270 165 240 180 180 285 195 285 165 180 105 180 60 165 15

arrow
true
0
Polygon -7500403 true true 150 0 0 150 105 150 105 293 195 293 195 150 300 150

box
false
0
Polygon -7500403 true true 150 285 285 225 285 75 150 135
Polygon -7500403 true true 150 135 15 75 150 15 285 75
Polygon -7500403 true true 15 75 15 225 150 285 150 135
Line -16777216 false 150 285 150 135
Line -16777216 false 150 135 15 75
Line -16777216 false 150 135 285 75

bug
true
0
Circle -7500403 true true 96 182 108
Circle -7500403 true true 110 127 80
Circle -7500403 true true 110 75 80
Line -7500403 true 150 100 80 30
Line -7500403 true 150 100 220 30

butterfly
true
0
Polygon -7500403 true true 150 165 209 199 225 225 225 255 195 270 165 255 150 240
Polygon -7500403 true true 150 165 89 198 75 225 75 255 105 270 135 255 150 240
Polygon -7500403 true true 139 148 100 105 55 90 25 90 10 105 10 135 25 180 40 195 85 194 139 163
Polygon -7500403 true true 162 150 200 105 245 90 275 90 290 105 290 135 275 180 260 195 215 195 162 165
Polygon -16777216 true false 150 255 135 225 120 150 135 120 150 105 165 120 180 150 165 225
Circle -16777216 true false 135 90 30
Line -16777216 false 150 105 195 60
Line -16777216 false 150 105 105 60

car
false
0
Polygon -7500403 true true 300 180 279 164 261 144 240 135 226 132 213 106 203 84 185 63 159 50 135 50 75 60 0 150 0 165 0 225 300 225 300 180
Circle -16777216 true false 180 180 90
Circle -16777216 true false 30 180 90
Polygon -16777216 true false 162 80 132 78 134 135 209 135 194 105 189 96 180 89
Circle -7500403 true true 47 195 58
Circle -7500403 true true 195 195 58

circle
false
0
Circle -7500403 true true 0 0 300

circle 2
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240

cow
false
0
Polygon -7500403 true true 200 193 197 249 179 249 177 196 166 187 140 189 93 191 78 179 72 211 49 209 48 181 37 149 25 120 25 89 45 72 103 84 179 75 198 76 252 64 272 81 293 103 285 121 255 121 242 118 224 167
Polygon -7500403 true true 73 210 86 251 62 249 48 208
Polygon -7500403 true true 25 114 16 195 9 204 23 213 25 200 39 123

cylinder
false
0
Circle -7500403 true true 0 0 300

dot
false
0
Circle -7500403 true true 90 90 120

face happy
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 255 90 239 62 213 47 191 67 179 90 203 109 218 150 225 192 218 210 203 227 181 251 194 236 217 212 240

face neutral
false
0
Circle -7500403 true true 8 7 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Rectangle -16777216 true false 60 195 240 225

face sad
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 168 90 184 62 210 47 232 67 244 90 220 109 205 150 198 192 205 210 220 227 242 251 229 236 206 212 183

fish
false
0
Polygon -1 true false 44 131 21 87 15 86 0 120 15 150 0 180 13 214 20 212 45 166
Polygon -1 true false 135 195 119 235 95 218 76 210 46 204 60 165
Polygon -1 true false 75 45 83 77 71 103 86 114 166 78 135 60
Polygon -7500403 true true 30 136 151 77 226 81 280 119 292 146 292 160 287 170 270 195 195 210 151 212 30 166
Circle -16777216 true false 215 106 30

flag
false
0
Rectangle -7500403 true true 60 15 75 300
Polygon -7500403 true true 90 150 270 90 90 30
Line -7500403 true 75 135 90 135
Line -7500403 true 75 45 90 45

flower
false
0
Polygon -10899396 true false 135 120 165 165 180 210 180 240 150 300 165 300 195 240 195 195 165 135
Circle -7500403 true true 85 132 38
Circle -7500403 true true 130 147 38
Circle -7500403 true true 192 85 38
Circle -7500403 true true 85 40 38
Circle -7500403 true true 177 40 38
Circle -7500403 true true 177 132 38
Circle -7500403 true true 70 85 38
Circle -7500403 true true 130 25 38
Circle -7500403 true true 96 51 108
Circle -16777216 true false 113 68 74
Polygon -10899396 true false 189 233 219 188 249 173 279 188 234 218
Polygon -10899396 true false 180 255 150 210 105 210 75 240 135 240

house
false
0
Rectangle -7500403 true true 45 120 255 285
Rectangle -16777216 true false 120 210 180 285
Polygon -7500403 true true 15 120 150 15 285 120
Line -16777216 false 30 120 270 120

leaf
false
0
Polygon -7500403 true true 150 210 135 195 120 210 60 210 30 195 60 180 60 165 15 135 30 120 15 105 40 104 45 90 60 90 90 105 105 120 120 120 105 60 120 60 135 30 150 15 165 30 180 60 195 60 180 120 195 120 210 105 240 90 255 90 263 104 285 105 270 120 285 135 240 165 240 180 270 195 240 210 180 210 165 195
Polygon -7500403 true true 135 195 135 240 120 255 105 255 105 285 135 285 165 240 165 195

line
true
0
Line -7500403 true 150 0 150 300

line half
true
0
Line -7500403 true 150 0 150 150

pentagon
false
0
Polygon -7500403 true true 150 15 15 120 60 285 240 285 285 120

person
false
0
Circle -7500403 true true 110 5 80
Polygon -7500403 true true 105 90 120 195 90 285 105 300 135 300 150 225 165 300 195 300 210 285 180 195 195 90
Rectangle -7500403 true true 127 79 172 94
Polygon -7500403 true true 195 90 240 150 225 180 165 105
Polygon -7500403 true true 105 90 60 150 75 180 135 105

plant
false
0
Rectangle -7500403 true true 135 90 165 300
Polygon -7500403 true true 135 255 90 210 45 195 75 255 135 285
Polygon -7500403 true true 165 255 210 210 255 195 225 255 165 285
Polygon -7500403 true true 135 180 90 135 45 120 75 180 135 210
Polygon -7500403 true true 165 180 165 210 225 180 255 120 210 135
Polygon -7500403 true true 135 105 90 60 45 45 75 105 135 135
Polygon -7500403 true true 165 105 165 135 225 105 255 45 210 60
Polygon -7500403 true true 135 90 120 45 150 15 180 45 165 90

square
false
0
Rectangle -7500403 true true 30 30 270 270

square 2
false
0
Rectangle -7500403 true true 30 30 270 270
Rectangle -16777216 true false 60 60 240 240

star
false
0
Polygon -7500403 true true 151 1 185 108 298 108 207 175 242 282 151 216 59 282 94 175 3 108 116 108

target
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240
Circle -7500403 true true 60 60 180
Circle -16777216 true false 90 90 120
Circle -7500403 true true 120 120 60

tree
false
0
Circle -7500403 true true 118 3 94
Rectangle -6459832 true false 120 195 180 300
Circle -7500403 true true 65 21 108
Circle -7500403 true true 116 41 127
Circle -7500403 true true 45 90 120
Circle -7500403 true true 104 74 152

triangle
false
0
Polygon -7500403 true true 150 30 15 255 285 255

triangle 2
false
0
Polygon -7500403 true true 150 30 15 255 285 255
Polygon -16777216 true false 151 99 225 223 75 224

truck
false
0
Rectangle -7500403 true true 4 45 195 187
Polygon -7500403 true true 296 193 296 150 259 134 244 104 208 104 207 194
Rectangle -1 true false 195 60 195 105
Polygon -16777216 true false 238 112 252 141 219 141 218 112
Circle -16777216 true false 234 174 42
Rectangle -7500403 true true 181 185 214 194
Circle -16777216 true false 144 174 42
Circle -16777216 true false 24 174 42
Circle -7500403 false true 24 174 42
Circle -7500403 false true 144 174 42
Circle -7500403 false true 234 174 42

turtle
true
0
Polygon -10899396 true false 215 204 240 233 246 254 228 266 215 252 193 210
Polygon -10899396 true false 195 90 225 75 245 75 260 89 269 108 261 124 240 105 225 105 210 105
Polygon -10899396 true false 105 90 75 75 55 75 40 89 31 108 39 124 60 105 75 105 90 105
Polygon -10899396 true false 132 85 134 64 107 51 108 17 150 2 192 18 192 52 169 65 172 87
Polygon -10899396 true false 85 204 60 233 54 254 72 266 85 252 107 210
Polygon -7500403 true true 119 75 179 75 209 101 224 135 220 225 175 261 128 261 81 224 74 135 88 99

wheel
false
0
Circle -7500403 true true 3 3 294
Circle -16777216 true false 30 30 240
Line -7500403 true 150 285 150 15
Line -7500403 true 15 150 285 150
Circle -7500403 true true 120 120 60
Line -7500403 true 216 40 79 269
Line -7500403 true 40 84 269 221
Line -7500403 true 40 216 269 79
Line -7500403 true 84 40 221 269

x
false
0
Polygon -7500403 true true 270 75 225 30 30 225 75 270
Polygon -7500403 true true 30 75 75 30 270 225 225 270

@#$#@#$#@
NetLogo 6.4
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
<experiments>
  <experiment name="baseline" repetitions="3" sequentialRunOrder="false" runMetricsEveryStep="true">
    <setup>setup</setup>
    <go>simulation</go>
    <timeLimit steps="120"/>
    <metric>count patches with [pcolor = green - 2]</metric>
    <metric>count cows</metric>
    <metric>pressure</metric>
    <metric>count cows with [owner = human 0]</metric>
    <metric>count cows with [owner = human 1]</metric>
    <metric>count cows with [owner = human 2]</metric>
    <enumeratedValueSet variable="cow-forage-requirement">
      <value value="2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="initial-grassland">
      <value value="100"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="initial-grass-growth-rate">
      <value value="0.001"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="fairness-concerning-me">
      <value value="0"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="fairness-concerning-others">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="cooperation-level">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="negative-reciprocity">
      <value value="0"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="positive-reciprocity">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="conformity-level">
      <value value="0"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="risk-aversion-level">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="agent0-backend">
      <value value="&quot;anthropic&quot;"/>
      <value value="&quot;openai&quot;"/>
      <value value="&quot;ollama&quot;"/>
      <value value="&quot;google&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="agent0-model">
      <value value="&quot;claude-sonnet-4-6&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="agent1-backend">
      <value value="&quot;anthropic&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="agent1-model">
      <value value="&quot;claude-sonnet-4-6&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="agent2-backend">
      <value value="&quot;anthropic&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="agent2-model">
      <value value="&quot;claude-sonnet-4-6&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="system-prompt-override">
      <value value="&quot;&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="memory-length">
      <value value="5"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="detect-institutions">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="institution-check-interval">
      <value value="5"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="condition">
      <value value="&quot;baseline&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="hybrid-fraction">
      <value value="0"/>
    </enumeratedValueSet>
  </experiment>
  <experiment name="full-gabm" repetitions="3" sequentialRunOrder="false" runMetricsEveryStep="true">
    <setup>setup</setup>
    <go>simulation</go>
    <timeLimit steps="120"/>
    <metric>count patches with [pcolor = green - 2]</metric>
    <metric>count cows</metric>
    <metric>pressure</metric>
    <metric>count cows with [owner = human 0]</metric>
    <metric>count cows with [owner = human 1]</metric>
    <metric>count cows with [owner = human 2]</metric>
    <enumeratedValueSet variable="cow-forage-requirement">
      <value value="2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="initial-grassland">
      <value value="100"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="initial-grass-growth-rate">
      <value value="0.001"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="fairness-concerning-me">
      <value value="0"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="fairness-concerning-others">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="cooperation-level">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="negative-reciprocity">
      <value value="0"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="positive-reciprocity">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="conformity-level">
      <value value="0"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="risk-aversion-level">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="agent0-backend">
      <value value="&quot;anthropic&quot;"/>
      <value value="&quot;openai&quot;"/>
      <value value="&quot;ollama&quot;"/>
      <value value="&quot;google&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="agent0-model">
      <value value="&quot;claude-sonnet-4-6&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="agent1-backend">
      <value value="&quot;anthropic&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="agent1-model">
      <value value="&quot;claude-sonnet-4-6&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="agent2-backend">
      <value value="&quot;anthropic&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="agent2-model">
      <value value="&quot;claude-sonnet-4-6&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="system-prompt-override">
      <value value="&quot;&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="memory-length">
      <value value="5"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="detect-institutions">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="institution-check-interval">
      <value value="5"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="condition">
      <value value="&quot;full-gabm&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="hybrid-fraction">
      <value value="0"/>
    </enumeratedValueSet>
  </experiment>
  <experiment name="hybrid-33" repetitions="3" sequentialRunOrder="false" runMetricsEveryStep="true">
    <setup>setup</setup>
    <go>simulation</go>
    <timeLimit steps="120"/>
    <metric>count patches with [pcolor = green - 2]</metric>
    <metric>count cows</metric>
    <metric>pressure</metric>
    <metric>count cows with [owner = human 0]</metric>
    <metric>count cows with [owner = human 1]</metric>
    <metric>count cows with [owner = human 2]</metric>
    <enumeratedValueSet variable="cow-forage-requirement">
      <value value="2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="initial-grassland">
      <value value="100"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="initial-grass-growth-rate">
      <value value="0.001"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="fairness-concerning-me">
      <value value="0"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="fairness-concerning-others">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="cooperation-level">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="negative-reciprocity">
      <value value="0"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="positive-reciprocity">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="conformity-level">
      <value value="0"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="risk-aversion-level">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="agent0-backend">
      <value value="&quot;anthropic&quot;"/>
      <value value="&quot;openai&quot;"/>
      <value value="&quot;ollama&quot;"/>
      <value value="&quot;google&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="agent0-model">
      <value value="&quot;claude-sonnet-4-6&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="agent1-backend">
      <value value="&quot;anthropic&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="agent1-model">
      <value value="&quot;claude-sonnet-4-6&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="agent2-backend">
      <value value="&quot;anthropic&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="agent2-model">
      <value value="&quot;claude-sonnet-4-6&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="system-prompt-override">
      <value value="&quot;&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="memory-length">
      <value value="5"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="detect-institutions">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="institution-check-interval">
      <value value="5"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="condition">
      <value value="&quot;hybrid&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="hybrid-fraction">
      <value value="0.33"/>
    </enumeratedValueSet>
  </experiment>
</experiments>
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180

@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
