-- Table: public.bag_reports

-- DROP TABLE IF EXISTS public.bag_reports;

CREATE TABLE IF NOT EXISTS public.bag_reports
(
    report_id text,
    colour text,
    bag_form text,
    shell text,
    brand text,
    weight_kg numeric(4,2),
    CONSTRAINT bag_reports_pkey PRIMARY KEY (report_id),
    CONSTRAINT bag_reports_bag_form_check CHECK (bag_form = ANY (ARRAY['backpack'::text, 'duffel'::text, 'suitcase'::text])),
    CONSTRAINT bag_reports_colour_check CHECK (length(colour) > 2),
    CONSTRAINT bag_reports_report_id_check CHECK (length(report_id) > 5),
    CONSTRAINT bag_reports_shell_check CHECK (shell = ANY (ARRAY['hard'::text, 'soft'::text, ''::text])),
    CONSTRAINT bag_reports_weight_kg_check CHECK (weight_kg > 0::numeric AND weight_kg < 32.01)
)