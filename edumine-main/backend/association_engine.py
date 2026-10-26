import pandas as pd
import numpy as np
from itertools import combinations
from typing import Dict, Any, List, Optional
from .data_engine import DataEngine

class AssociationEngine:
    def __init__(self, data_engine: DataEngine):
        self.data_engine = data_engine

    def _discretize_data(self) -> pd.DataFrame:
        df = self.data_engine.processed_df.copy()
        if df is None or len(df) == 0:
            return pd.DataFrame()

        binned = pd.DataFrame()
        cols = {c.lower(): c for c in df.columns}
        metadata = self.data_engine.column_metadata or {}

        # 1. Attendance or Absences
        att_c = next((cols[k] for k in cols if 'attend' in k), None)
        abs_c = next((cols[k] for k in cols if 'absence' in k), None)
        if att_c and att_c in df.columns:
            binned['Attendance'] = pd.cut(
                df[att_c], 
                bins=[-np.inf, 72, 85, np.inf], 
                labels=['Low Attendance (<72%)', 'Moderate Attendance (72-85%)', 'High Attendance (>85%)']
            )
        elif abs_c and abs_c in df.columns:
            binned['Absences'] = pd.cut(
                df[abs_c],
                bins=[-np.inf, 2, 7, np.inf],
                labels=['Low Absences (Regular)', 'Moderate Absences (3-7)', 'High Absences (>7 days)']
            )

        # 2. Study Time / Study Hours
        study_c = next((cols[k] for k in cols if 'study' in k or 'hours' in k), None)
        if study_c and study_c in df.columns:
            max_s = df[study_c].max()
            if max_s <= 5:  # e.g., 1-4 scale from UCI dataset
                study_map = {
                    1: 'Minimal Study (<2h/wk)',
                    2: 'Moderate Study (2-5h/wk)',
                    3: 'Diligent Study (5-10h/wk)',
                    4: 'Intensive Study (>10h/wk)'
                }
                binned['StudyHours'] = df[study_c].map(study_map).fillna('Moderate Study (2-5h/wk)')
            else:
                binned['StudyHours'] = pd.cut(
                    df[study_c],
                    bins=[-np.inf, 8, 18, np.inf],
                    labels=['Low Study (<8h/wk)', 'Moderate Study (8-18h/wk)', 'High Study (>18h/wk)']
                )

        # 3. Failures / Arrears / Backlogs
        fail_c = next((cols[k] for k in cols if 'fail' in k or 'arrear' in k or 'backlog' in k), None)
        if fail_c and fail_c in df.columns:
            binned['PriorFailures'] = df[fail_c].apply(lambda x: 'Prior Failures (>=1)' if x > 0 else 'Zero Failures')

        # 4. Midterm / Early Period Exam (e.g. G1, G2, Midterm, Quiz)
        mid_c = next((cols[k] for k in cols if 'midterm' in k or 'quiz' in k or k in ['g1', 'g2']), None)
        if mid_c and mid_c in df.columns:
            max_m = df[mid_c].max()
            if max_m <= 20:
                binned['MidtermScore'] = pd.cut(
                    df[mid_c],
                    bins=[-np.inf, 9.5, 13.5, np.inf],
                    labels=['Low Midterm (<10)', 'Average Midterm (10-13)', 'High Midterm (>=14)']
                )
            else:
                binned['MidtermScore'] = pd.cut(
                    df[mid_c],
                    bins=[-np.inf, 55, 75, np.inf],
                    labels=['Low Midterm (<55)', 'Average Midterm (55-75)', 'High Midterm (>75)']
                )

        # 5. Assignments / Continuous Assessment
        assign_c = next((cols[k] for k in cols if 'assign' in k or 'homework' in k), None)
        if assign_c and assign_c in df.columns:
            binned['Assignment'] = pd.cut(
                df[assign_c], 
                bins=[-np.inf, 60, 80, np.inf], 
                labels=['Low Assignment (<60%)', 'Average Assignment (60-80%)', 'High Assignment (>80%)']
            )

        # 6. LMS Engagement
        lms_c = next((cols[k] for k in cols if 'lms' in k or 'login' in k), None)
        if lms_c and lms_c in df.columns:
            binned['LMSEngagement'] = pd.cut(
                df[lms_c], 
                bins=[-np.inf, 6, 14, np.inf], 
                labels=['Low LMS Usage (<6h)', 'Regular LMS Usage (6-14h)', 'High LMS Usage (>14h)']
            )

        # 7. Final Exam Score / Performance
        reg_c = metadata.get('reg_target')
        if reg_c and reg_c in df.columns:
            max_f = df[reg_c].max()
            if max_f <= 20:
                binned['FinalPerformance'] = pd.cut(
                    df[reg_c],
                    bins=[-np.inf, 9.5, 13.5, np.inf],
                    labels=['Performance: Low (<10)', 'Performance: Moderate (10-13)', 'Performance: High (>=14)']
                )
            elif max_f <= 4.0:
                binned['FinalPerformance'] = pd.cut(
                    df[reg_c],
                    bins=[-np.inf, 2.0, 3.2, np.inf],
                    labels=['Performance: Low (<2.0)', 'Performance: Moderate (2.0-3.2)', 'Performance: High (>3.2)']
                )
            else:
                binned['FinalPerformance'] = pd.cut(
                    df[reg_c],
                    bins=[-np.inf, 55, 75, np.inf],
                    labels=['Performance: Low (<55)', 'Performance: Moderate (55-75)', 'Performance: High (>75)']
                )

        # 8. Academic Risk Status (Target)
        risk_c = metadata.get('class_target')
        if risk_c and risk_c in df.columns:
            binned['AcademicRisk'] = df[risk_c].astype(str).apply(
                lambda x: 'Status: At-Risk' if any(w in x.lower() for w in ['risk', 'fail', '1', 'yes', 'true']) else 'Status: Safe'
            )

        # 9. Important Educational Categoricals (binary or low cardinality)
        already_used = set([c.lower() for c in [att_c, abs_c, study_c, fail_c, mid_c, assign_c, lms_c, reg_c, risk_c] if c])
        cat_candidates = ['higher', 'schoolsup', 'famsup', 'paid', 'activities', 'internet', 'romantic', 'parent_education', 'department', 'gender', 'medu', 'fedu', 'walc']

        for c in df.columns:
            c_low = c.lower()
            if c_low in already_used or c_low in ['id', 'student_id', 'name', 'stuid', 'academic_risk']:
                continue

            uniq = df[c].dropna().unique()
            is_cand = any(k in c_low for k in cat_candidates) or (2 <= len(uniq) <= 3)
            if is_cand and len(uniq) <= 4:
                col_label = c.replace('_', ' ').title()
                if set(map(str.lower, map(str, uniq))).issubset({'yes', 'no'}):
                    binned[col_label] = df[c].astype(str).apply(lambda v: f"{col_label}: Yes" if v.lower() == 'yes' else f"{col_label}: No")
                elif len(uniq) <= 4:
                    binned[col_label] = df[c].astype(str).apply(lambda v: f"{col_label}: {v}")

        return binned

    def _mine_rules_native(self, df_binned: pd.DataFrame, min_support: float = 0.08, min_confidence: float = 0.5, min_lift: float = 1.1) -> List[Dict[str, Any]]:
        """High-performance, pure-Python association rule mining."""
        n = len(df_binned)
        if n == 0:
            return []

        # Convert to transactions
        transactions = []
        for _, row in df_binned.iterrows():
            tx = set([f"{col}={val}" for col, val in row.items() if pd.notnull(val)])
            transactions.append(tx)

        # Count 1-itemsets
        item_counts = {}
        for tx in transactions:
            for item in tx:
                item_counts[frozenset([item])] = item_counts.get(frozenset([item]), 0) + 1

        frequent_itemsets = {itemset: count for itemset, count in item_counts.items() if (count / n) >= min_support}

        # 2-itemsets
        item_list = [list(k)[0] for k in frequent_itemsets.keys()]
        pair_counts = {}
        for tx in transactions:
            valid_items = [i for i in item_list if i in tx]
            for u, v in combinations(valid_items, 2):
                pair = frozenset([u, v])
                pair_counts[pair] = pair_counts.get(pair, 0) + 1

        for pair, count in pair_counts.items():
            if (count / n) >= min_support:
                frequent_itemsets[pair] = count

        # 3-itemsets
        triplet_counts = {}
        for tx in transactions:
            valid_items = [i for i in item_list if i in tx]
            for comb in combinations(valid_items, 3):
                triplet = frozenset(comb)
                triplet_counts[triplet] = triplet_counts.get(triplet, 0) + 1

        for triplet, count in triplet_counts.items():
            if (count / n) >= min_support:
                frequent_itemsets[triplet] = count

        # Generate Rules
        rules = []
        for itemset, count_both in frequent_itemsets.items():
            if len(itemset) < 2:
                continue
            support_both = count_both / n

            for r in range(1, len(itemset)):
                for antecedent in combinations(itemset, r):
                    ant_set = frozenset(antecedent)
                    con_set = itemset - ant_set

                    ant_cols = set(i.split('=', 1)[0] for i in ant_set)
                    con_cols = set(i.split('=', 1)[0] for i in con_set)
                    if ant_cols & con_cols:
                        continue

                    # Avoid tautological cross-links between AcademicRisk and FinalPerformance
                    if ('AcademicRisk' in ant_cols and 'FinalPerformance' in con_cols) or \
                       ('FinalPerformance' in ant_cols and 'AcademicRisk' in con_cols):
                        continue

                    if ant_set in frequent_itemsets and con_set in frequent_itemsets:
                        support_ant = frequent_itemsets[ant_set] / n
                        support_con = frequent_itemsets[con_set] / n

                        confidence = support_both / support_ant
                        lift = confidence / support_con if support_con > 0 else 0

                        if confidence >= min_confidence and lift >= min_lift:
                            # Format for display
                            ant_labels = [i.split('=', 1)[1] if '=' in i else i for i in ant_set]
                            con_labels = [i.split('=', 1)[1] if '=' in i else i for i in con_set]

                            # Prioritize rules concluding in AcademicRisk or low performance, where outcome is the consequent
                            con_str = " ".join(con_labels)
                            ant_str = " ".join(ant_labels)
                            is_risk_consequent = ('At-Risk' in con_str or 'Performance: Low' in con_str) and not ('Status:' in ant_str)
                            is_outcome_consequent = ('Status:' in con_str or 'Performance:' in con_str) and not ('Status:' in ant_str)

                            rules.append({
                                'antecedents': sorted(ant_labels),
                                'consequents': sorted(con_labels),
                                'antecedent_str': " AND ".join(sorted(ant_labels)),
                                'consequent_str': " AND ".join(sorted(con_labels)),
                                'support': round(float(support_both), 4),
                                'confidence': round(float(confidence), 4),
                                'lift': round(float(lift), 3),
                                'leverage': round(float(support_both - (support_ant * support_con)), 4),
                                'is_risk_related': is_risk_consequent,
                                'is_outcome_consequent': is_outcome_consequent
                            })

        # Sort by is_risk_related descending, then is_outcome_consequent descending, then lift descending
        rules.sort(key=lambda x: (x['is_risk_related'], x['is_outcome_consequent'], x['lift'], x['confidence']), reverse=True)
        return rules[:50]

    def mine_rules(self, min_support: float = 0.08, min_confidence: float = 0.5, min_lift: float = 1.1) -> Dict[str, Any]:
        df_binned = self._discretize_data()
        rules = self._mine_rules_native(df_binned, min_support=min_support, min_confidence=min_confidence, min_lift=min_lift)

        # Adaptive fallback: If user thresholds return 0 rules, automatically relax thresholds slightly
        effective_support = min_support
        effective_confidence = min_confidence
        effective_lift = min_lift

        if not rules:
            for s_factor in [0.6, 0.4]:
                relaxed_s = max(0.03, round(min_support * s_factor, 2))
                relaxed_c = max(0.35, round(min_confidence - 0.1, 2))
                relaxed_l = max(1.05, round(min_lift - 0.1, 2))
                fallback_rules = self._mine_rules_native(df_binned, min_support=relaxed_s, min_confidence=relaxed_c, min_lift=relaxed_l)
                if fallback_rules:
                    rules = fallback_rules
                    effective_support = relaxed_s
                    effective_confidence = relaxed_c
                    effective_lift = relaxed_l
                    break

        # Generate network graph nodes and links for visualization
        nodes = []
        links = []
        node_ids = set()

        for idx, r in enumerate(rules[:15]):
            rule_id = f"R{idx+1}"
            nodes.append({
                'id': rule_id,
                'name': f"Rule #{idx+1} (Lift: {r['lift']})",
                'type': 'rule',
                'size': int(r['lift'] * 12)
            })

            for ant in r['antecedents']:
                if ant not in node_ids:
                    nodes.append({'id': ant, 'name': ant, 'type': 'antecedent', 'size': 10})
                    node_ids.add(ant)
                links.append({'source': ant, 'target': rule_id})

            for con in r['consequents']:
                if con not in node_ids:
                    nodes.append({'id': con, 'name': con, 'type': 'consequent', 'size': 16})
                    node_ids.add(con)
                links.append({'source': rule_id, 'target': con})

        return {
            'total_rules_found': len(rules),
            'min_support': effective_support,
            'min_confidence': effective_confidence,
            'min_lift': effective_lift,
            'rules': rules,
            'network_graph': {
                'nodes': nodes,
                'links': links
            }
        }
